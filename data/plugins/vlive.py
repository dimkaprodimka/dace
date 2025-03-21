#-plugin-sig:h7zHBpE+sz+/j+dKlpS8Of0omqH96Sr9IDi1NWAyYKNoK291a+oL4iJD2A6HcgrlMwFQSVkdZBXA2BugMLbvda/VyIGOvc47YBgBWKAuU0NicKfvrZK2PNAGho9uwC2Ae241ONKJAQOU5FTGU18mfJ+cL289XP+S7M+sZ6C63UF3O/gvn6GIW0aiCZ653Ny2AQ/FjkgFsdlIlD66x9eNulrbyXyp5jjRBbDSlMvxI8vSDzY9LFWW7TFSIJeiobJmETR9sq069jaw1624HOiIhWYlwEtbGXYKtU6rynb0xlouayttLutz2CRVLljf7Bi6e7m3wHdnUF+WozQrJZHJFQ==
import re
import json

from ACEStream.PluginsContainer.streamlink.plugin import Plugin, PluginError
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class Vlive(Plugin):
    _url_re = re.compile(r"https?://(?:www.)vlive\.tv/video/(\d+)")
    _video_status = re.compile(r'oVideoStatus = (.+)<', re.DOTALL)
    _video_init_url = "https://www.vlive.tv/video/init/view"

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    @property
    def video_id(self):
        return self._url_re.match(self.url).group(1)

    def _get_streams(self):
        vinit_req = self.session.http.get(self._video_init_url,
                                          params=dict(videoSeq=self.video_id),
                                          headers=dict(referer=self.url))
        if vinit_req.status_code != 200:
            raise PluginError('Could not get video init page (HTTP Status {})'
                              .format(vinit_req.status_code))

        video_status_js = self._video_status.search(vinit_req.text)
        if not video_status_js:
            raise PluginError('Could not find video status information!')

        video_status = json.loads(video_status_js.group(1))

        if video_status['viewType'] == 'vod':
            raise PluginError('VODs are not supported')

        if 'liveStreamInfo' not in video_status:
            raise PluginError('Stream is offline')

        stream_info = json.loads(video_status['liveStreamInfo'])

        streams = dict()
        # All "resolutions" have a variant playlist with only one entry, so just combine them
        for i in stream_info['resolutions']:
            res_streams = HLSStream.parse_variant_playlist(self.session, i['cdnUrl'])
            if len(res_streams.values()) > 1:
                self.logger.warning('More than one stream in variant playlist, using first entry!')

            streams[i['name']] = res_streams.popitem()[1]

        return streams


__plugin__ = Vlive
