#-plugin-sig:a7keDIRPUl0PBrG2DHIhsCHH4rT1yoFdxo3+5kzWZjj6wmoEnU8Pp6Ikx7UHGzAJN+o6lMd9Dn984JadxIJchkmCfO2R2MQyz1MnqsR/5A6s3udRAUGJRu4kKl1EyK9XLqXHI2jj17Vlo7yNXRexKBKH4vXZ1NeOzs2az745BvBiaxpzLsQnWH9/YtfZBbkdFrO9bBtu/swT52GSoLEJGl4kKZtf0v38KYEZjJml0vaAuO8O+5s5vuCQt5p1qabUM8BiKa27y9ku9Nijyqqr8ghvtnVUmAt1Tp+XsYwKl8aW7A7+QNUSm6Pugl6gmrLU5kneY0H3UUGo7IVFRVvh3A==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin, PluginError
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.compat import unquote_plus, is_py3


QUALITY_WEIGHTS = {
    "src": 1080,
}


class DLive(Plugin):
    """
    Plugin for dlive.tv
    """

    _url_re = re.compile(r"https?://(?:www\.)?dlive\.tv/")
    _playback_re = re.compile(r"""(?<=playbackUrl":")(.+?)(?=")""")
    _livestream_re = re.compile(r""""livestream":null""")
    _username_re = re.compile(r"(?<=user:)(\w|-)+")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    @classmethod
    def stream_weight(cls, key):
        weight = QUALITY_WEIGHTS.get(key)
        if weight:
            return weight, "dlive"

        return Plugin.stream_weight(key)

    def _get_streams(self):
        res = self.session.http.get(self.url)

        m = self._playback_re.search(res.text)

        if m:
            hls_url = m.group(0)

            if is_py3:
                hls_url = bytes(unquote_plus(hls_url), "utf-8").decode(
                    "unicode_escape")
            else:
                hls_url = unquote_plus(hls_url).decode("unicode_escape")
        else:
            if self._livestream_re.search(res.text) is not None:
                raise PluginError('Stream is offline')

            m = self._username_re.search(res.text)
            if m:
                hls_url = "https://live.prd.dlive.tv/hls/live/{}.m3u8".format(
                    m.group(0))
            else:
                raise PluginError('Could not find username')

        return HLSStream.parse_variant_playlist(self.session, hls_url)


__plugin__ = DLive
