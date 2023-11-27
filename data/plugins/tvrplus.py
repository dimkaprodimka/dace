#-plugin-sig:ShfkH7SBxWcNzavfe3zI2NiCN4kQP8N1ruk4DFxDhVrfGmFguciK6W4c7WEZ9K+E59YSwdHIDLXuCYskdhmhPR1VPNpGdqq6Uo7E+ewvYefe4iE7nY9OJk1PDcdr/3UtDTdbSUo+RSxR7VL5wCGnKf02vVhZj6uiC48LfOJFc+fwzVK9zFZU3D8L1pOjIdsDL+LYxZBtLRolCSANoAqMYgJVUYqoDIuG19jfGCT2VK9ABHoVd/rX8xYXVhxYCH3Pz+vvj6RuCj8Jhq8ObIUoi0ChlKlBjxMhWdDTbmgZbctiDHYhvxLuGiFn7mrTSLYkZnwixkRB/VA20KEeGAA0Xw==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class TVRPlus(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?tvrplus\.ro/live/")
    hls_file_re = re.compile(r"""["'](?P<url>[^"']+\.m3u8(?:[^"']+)?)["']""")

    stream_schema = validate.Schema(
        validate.all(
            validate.transform(hls_file_re.findall),
            validate.any(None, [validate.text])
        ),
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        headers = {
            "User-Agent": useragents.FIREFOX,
            "Referer": self.url
        }
        stream_url = self.stream_schema.validate(self.session.http.get(self.url).text)
        if stream_url:
            stream_url = list(set(stream_url))
            for url in stream_url:
                self.logger.debug("URL={0}".format(url))
                for s in HLSStream.parse_variant_playlist(self.session, url, headers=headers).items():
                    yield s


__plugin__ = TVRPlus
