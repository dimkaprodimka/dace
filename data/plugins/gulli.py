#-plugin-sig:YkN0zh2jQLOmZHl49icOcbpzSMS5WGaTAZHjDV6neDXPmELMFzMhAhB751o0Zh9p5R2f03m5+Y0AZ5xlOtIQ58Ol53ClJ1jtl83p6okl+Sr8Uzmc7Pjh2B9W+PmpI85oP6sDn8Tmdczz37QcMjh2Rbxb2o48Ht4MGJi0kDNMR9jXMnTiblgjVOitv/x0Xx4Z8IxB5f3AlUHN4vAkh9kUYPBnIMJcwdch8T7X/hEKEOjhU/BPaR6x+G3wuD2qqA7RBGGZDm0u/ak7m/p0dTcIRpstxDsJfoHNvrojY8Yzg0QEIVXuHEDujXvVj/G5QuQBnsZOVSSV2RJOHVD0+7Wj9A==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream, HTTPStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json


class Gulli(Plugin):
    LIVE_PLAYER_URL = 'https://replay.gulli.fr/jwplayer/embedstreamtv'
    VOD_PLAYER_URL = 'https://replay.gulli.fr/jwplayer/embed/{0}'

    _url_re = re.compile(r'https?://replay\.gulli\.fr/(?:Direct|.+/(?P<video_id>VOD[0-9]+))')
    _playlist_re = re.compile(r'sources: (\[.+?\])', re.DOTALL)
    _vod_video_index_re = re.compile(r'jwplayer\(idplayer\).playlistItem\((?P<video_index>[0-9]+)\)')
    _mp4_bitrate_re = re.compile(r'.*_(?P<bitrate>[0-9]+)\.mp4')

    _video_schema = validate.Schema(
        validate.all(
            validate.transform(lambda x: re.sub(r'"?file"?:\s*[\'"](.+?)[\'"],?', r'"file": "\1"', x, flags=re.DOTALL)),
            validate.transform(lambda x: re.sub(r'"?\w+?"?:\s*function\b.*?(?<={).*(?=})', "", x, flags=re.DOTALL)),
            validate.transform(parse_json),
            [
                validate.Schema({
                    'file': validate.url()
                })
            ]
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return Gulli._url_re.match(url)

    def _get_streams(self):
        match = self._url_re.match(self.url)
        video_id = match.group('video_id')
        if video_id is not None:
            # VOD
            live = False
            player_url = self.VOD_PLAYER_URL.format(video_id)
        else:
            # Live
            live = True
            player_url = self.LIVE_PLAYER_URL

        res = self.session.http.get(player_url)
        playlist = re.findall(self._playlist_re, res.text)
        index = 0
        if not live:
            # Get the index for the video on the playlist
            match = self._vod_video_index_re.search(res.text)
            if match is None:
                return
            index = int(match.group('video_index'))

        if not playlist:
            return
        videos = self._video_schema.validate(playlist[index])

        for video in videos:
            video_url = video['file']

            # Ignore non-supported MSS streams
            if 'isml/Manifest' in video_url:
                continue

            try:
                if '.m3u8' in video_url:
                    for stream in HLSStream.parse_variant_playlist(self.session, video_url).items():
                        yield stream
                elif '.mp4' in video_url:
                    match = self._mp4_bitrate_re.match(video_url)
                    if match is not None:
                        bitrate = '%sk' % match.group('bitrate')
                    else:
                        bitrate = 'vod'
                    yield bitrate, HTTPStream(self.session, video_url)
            except IOError as err:
                if '403 Client Error' in str(err):
                    self.logger.error('Failed to access stream, may be due to geo-restriction')
                raise


__plugin__ = Gulli
