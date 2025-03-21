#-plugin-sig:RK5mQYLqYdcp4MiJAQz4Up2AkWdQZaBUF0nRhdsPv1XfUShegi7/qsgDWg23pjE0Z4atJex8bNmousz0kLBNkpYJ/GhWjbCIbk4bqd0Ns6qyG0IFTbmrelyLC1Lj4jgauLF2ewnvwqsyYbtnGML7PF0QEAFwDjJiP+3SHY0GTbvJavYp3Q+wbm/mNjizGF9VEEOSwlQeixjfCjfUKs/j6YaLXJaHTi4Elh9l9wRNzv7InLadOLiAaicwiGEzoq6k30i7o3waCV8j5WG0RTxHPfHDWe8TFmktXZId4hfdgMzPddDunTga/WWZJ6Kgetj48aIS/riSpB6ZyuR94O1qtQ==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink import NoStreamsError


class CubeTV(Plugin):
    _url_re = re.compile(r"https?://(www\.)?cube\.tv/(?P<channel>[^/]{2,})")

    _channel_info_api_url_base = "https://www.cube.tv/studio/info?cube_id={channel}"
    _stream_data_api_url_base = "https://www.cube.tv/studioApi/getStudioSrcBySid?sid={gid}&videoType=1&https=1"

    _channel_info_schema = validate.Schema({
        u"code": 1,
        u"msg": u"success",
        u"data": {
            u"gid": validate.text,
            u"cube_id": validate.text
        }
    })

    _stream_data_schema = validate.Schema({
        u"code": 1,
        u"msg": u"success",
        u"data": {
            u"video": u"hls",
            u"video_src": validate.url()
        }
    })

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_api_res(self, user_id):
        try:
            res = self.session.http.get(self._channel_info_api_url_base.format(channel=user_id))
            return res
        except Exception:
            raise NoStreamsError(self.url)

    def _get_streams(self):
        user_id = self._url_re.match(self.url).group(2)
        res = self._get_api_res(user_id)
        user_gid = self.session.http.json(res, schema=self._channel_info_schema)['data']['gid']

        try:
            stream_data = self.session.http.get(self._stream_data_api_url_base.format(gid=user_gid))
            hls = self.session.http.json(stream_data, schema=self._stream_data_schema)['data']['video_src']
        except Exception:
            raise NoStreamsError(self.url)

        return HLSStream.parse_variant_playlist(self.session, hls)


__plugin__ = CubeTV
