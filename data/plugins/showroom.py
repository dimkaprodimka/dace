# -*- coding: utf-8 -*-
#-plugin-sig:eKU7LR6eAMn4rFOwI2z6z0gR9aFmnmbREuTaT3C98QOxZVo1NVxrnbUdfpzRtqzg6OdHLdu5UvYCyu5++x6JwiFMJopRSGdizn4Z6mgYYCBp7xEEb+UqUBcO7l2aeAI/5ZLEgsiILbike7KYtrSCNUFk9qFprXdRlZ4J5d8iL5Rez0lAqjNnyCCuW/TUTjb7N7U7uuXck8sWGTr9pwHukEknZlIpqYHroTjnN+jg8bQ1gyU9AdUhNK+a/X1yQkPIwbtTL5F99WRLfVj3lRpxWX0gT9NHzSDOb64xn+gyqwJY/Ps9J+VqKLD9dQSa19YuiR0z2i6Smwf8whNM4WucmA==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate, useragents
from ACEStream.PluginsContainer.streamlink.stream import HLSStream, RTMPStream
from ACEStream.PluginsContainer.streamlink.stream.hls import HLSStreamReader, HLSStreamWorker

_url_re = re.compile(r'''^https?://
    (?:\w*.)?
    showroom-live.com/
    (?:
        (?P<room_title>[\w-]+$)
        |
        room/profile\?room_id=(?P<room_id>\d+)$
    )
''', re.VERBOSE)

_room_id_re = re.compile(r'"roomId":(?P<room_id>\d+),')
_room_id_alt_re = re.compile(r'content="showroom:///room\?room_id=(?P<room_id>\d+)"')
_room_id_lookup_failure_log = 'Failed to find room_id for {0} using {1} regex'

_api_status_url = 'https://www.showroom-live.com/room/is_live?room_id={room_id}'
_api_stream_url = 'https://www.showroom-live.com/api/live/streaming_url?room_id={room_id}'

_api_stream_schema = validate.Schema(
    validate.any({
        "streaming_url_list": validate.all([
            {
                "url": validate.text,
                validate.optional("stream_name"): validate.text,
                "id": int,
                "label": validate.text,
                "is_default": int,
                "type": validate.text,
                "quality": int,
            }
        ])
    },
        {}
    )
)

# the "low latency" streams are rtmp, the others are hls
_rtmp_quality_lookup = {
    "オリジナル画質": "high",
    "オリジナル画質(低遅延)": "high",
    "original spec(low latency)": "high",
    "original spec": "high",
    "低画質": "low",
    "低画質(低遅延)": "low",
    "low spec(low latency)": "low",
    "low spec": "low"
}
# changes here must also be updated in test_plugin_showroom
_quality_weights = {
    "high": 720,
    "other": 360,
    "low": 160
}
# pages that definitely aren't rooms
_info_pages = set((
    "onlive",
    "campaign",
    "timetable",
    "event",
    "news",
    "article",
    "ranking",
    "follow",
    "search",
    "mypage",
    "payment",
    "user",
    "notice",
    "s",
    "organizer_registration",
    "lottery"
))


class ShowroomHLSStreamWorker(HLSStreamWorker):
    def _playlist_reload_time(self, playlist, sequences):
        return 1.5


class ShowroomHLSStreamReader(HLSStreamReader):
    __worker__ = ShowroomHLSStreamWorker


class ShowroomHLSStream(HLSStream):
    def open(self):
        reader = ShowroomHLSStreamReader(self)
        reader.open()

        return reader


class Showroom(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        match = _url_re.match(url)
        if not match or match.group("room_title") in _info_pages:
            return False
        return True

    @classmethod
    def stream_weight(cls, stream):
        if stream in _quality_weights:
            return _quality_weights.get(stream), "quality"

        return Plugin.stream_weight(stream)

    def __init__(self, url):
        Plugin.__init__(self, url)
        self._headers = {
            'Referer': self.url,
            'User-Agent': useragents.FIREFOX
        }
        self._room_id = None
        self._stream_urls = None

    @property
    def room_id(self):
        if self._room_id is None:
            self._room_id = self._get_room_id()
        return self._room_id

    def _get_room_id(self):
        """
        Locates unique identifier ("room_id") for the room.

        Returns the room_id as a string, or None if no room_id was found
        """
        match_dict = _url_re.match(self.url).groupdict()

        if match_dict['room_id'] is not None:
            return match_dict['room_id']
        else:
            res = self.session.http.get(self.url, headers=self._headers)
            match = _room_id_re.search(res.text)
            if not match:
                title = self.url.rsplit('/', 1)[-1]
                self.logger.debug(_room_id_lookup_failure_log.format(title, 'primary'))
                match = _room_id_alt_re.search(res.text)
                if not match:
                    self.logger.debug(_room_id_lookup_failure_log.format(title, 'secondary'))
                    return  # Raise exception?
            return match.group('room_id')

    def _get_stream_info(self, room_id):
        res = self.session.http.get(_api_stream_url.format(room_id=room_id), headers=self._headers)
        return self.session.http.json(res, schema=_api_stream_schema)

    def _get_rtmp_stream(self, stream_info):
        rtmp_url = '/'.join((stream_info['url'], stream_info['stream_name']))
        quality = _rtmp_quality_lookup.get(stream_info['label'], "other")

        params = dict(rtmp=rtmp_url, live=True)
        return quality, RTMPStream(self.session, params=params)

    def _get_streams(self):
        info = self._get_stream_info(self.room_id)
        if not info:
            return

        for stream_info in info.get("streaming_url_list", []):
            if stream_info["type"] == "rtmp":
                yield self._get_rtmp_stream(stream_info)
            elif stream_info["type"] == "hls":
                streams = ShowroomHLSStream.parse_variant_playlist(self.session, stream_info["url"])
                if not streams:
                    quality = _rtmp_quality_lookup.get(stream_info["label"], "other")
                    yield quality, ShowroomHLSStream(self.session, stream_info["url"])
                else:
                    for s in streams.items():
                        yield s


__plugin__ = Showroom
