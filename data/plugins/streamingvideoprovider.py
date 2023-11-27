#-plugin-sig:feaLEeWf+FmtHSNL7hacnmc8qkGe1sxMeitgkwQBSC6WcijzpUYk6fd0tlNDTnQVCQ06Yft6CkbAzKIs9r13h8Vv5JzSr15uORqOxyz5sFNsIIBq6bbfybpWkViz1rkG4111Xf7uh2A1SdgWbeDhPYPuL4E/cI4uI2cFHOZ+EqY/MY4BDfNnwzenMgm5OAl5N1R8BTKwVwWfwDDckzA/sP5JGCnebQoSKtDfDisgdiLGjLnZ8FsEyzrnTLbcVg4Irta5ZAh5UfA3le56Q/nCVw/l5iFjpcwQ3d5lmi0g1lWT//A8mNqQ775cYnA3NOdB7ZhA5trnp4bLFTayaz4iuw==
import re

from time import time

from ACEStream.PluginsContainer.streamlink.plugin import Plugin, PluginError
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import RTMPStream, HLSStream

SWF_URL = "http://play.streamingvideoprovider.com/player2.swf"
API_URL = "http://player.webvideocore.net/index.php"

_url_re = re.compile(
    r"http(s)?://(\w+\.)?streamingvideoprovider.co.uk/(?P<channel>[^/&?]+)"
)
_hls_re = re.compile(r"'(http://.+\.m3u8)'")

_rtmp_schema = validate.Schema(
    validate.xml_findtext("./info/url"),
    validate.url(scheme="rtmp")
)
_hls_schema = validate.Schema(
    validate.transform(_hls_re.search),
    validate.any(
        None,
        validate.all(
            validate.get(1),
            validate.url(
                scheme="http",
                path=validate.endswith("m3u8")
            )
        )
    )
)


class Streamingvideoprovider(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_hls_stream(self, channel_name):
        params = {
            "l": "info",
            "a": "ajax_video_info",
            "file": channel_name,
            "rid": time()
        }
        playlist_url = self.session.http.get(API_URL, params=params, schema=_hls_schema)
        if not playlist_url:
            return

        return HLSStream(self.session, playlist_url)

    def _get_rtmp_stream(self, channel_name):
        params = {
            "l": "info",
            "a": "xmlClipPath",
            "clip_id": channel_name,
            "rid": time()
        }
        res = self.session.http.get(API_URL, params=params)
        rtmp_url = self.session.http.xml(res, schema=_rtmp_schema)

        return RTMPStream(self.session, {
            "rtmp": rtmp_url,
            "swfVfy": SWF_URL,
            "live": True
        })

    def _get_streams(self):
        match = _url_re.match(self.url)
        channel_name = match.group("channel")

        try:
            stream = self._get_rtmp_stream(channel_name)
            yield "live", stream
        except PluginError as err:
            self.logger.error("Unable to extract RTMP stream: {0}", err)

        try:
            stream = self._get_hls_stream(channel_name)
            if stream:
                yield "live", stream
        except PluginError as err:
            self.logger.error("Unable to extract HLS stream: {0}", err)


__plugin__ = Streamingvideoprovider
