#-plugin-sig:VygDQcrC49a2YDTyhUA6OhpQ1sXSxi0c6dQ+2TdV8t9QLNi1x7GN06LUPkRe39ifg4jlgF1LRzfkJq7urRTp2EW+06sVCHDsjyspBp//s7ae/9oyLWJQfFLAqFZw1YTq8DYgFXhCTRLz3d9ybj9z0UlwHAIHRuUnzKKZJM8lFqJbTtn+rCS/aDi1Iu5zXCzdr/w+XJksg5joCL+iKd10pVBt8HCikDU+9bvNGe0YzhTyjLMXXf4GgVlPUPQ+mBWXzgs/BEmrZVfSeCx9aXsXsLxTFqeTi9MERZWKn9HsnHQgk79CBYPksU3jv+gf7VnZIZRp0gU2NXZx1vQmt4do2A==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class WebcastIndiaGov(Plugin):
    _url_re = re.compile(r'https?://(?:www\.)?webcast.gov.in/.+')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        try:
            url_content = ""
            self.session.http.headers = {'User-Agent': useragents.ANDROID}
            if "#channel" in self.url.lower():
                requested_channel = self.url.lower()[self.url.lower().index('#channel') + 8:]
                url_content = self.session.http.get('http://webcast.gov.in/mobilevideo.asp?id=div' + requested_channel).text
            else:
                url_content = self.session.http.get(self.url).text
            hls_url = url_content[: url_content.rindex('master.m3u8') + 11]
            hls_url = hls_url[hls_url.rindex('"') + 1:]
            return HLSStream.parse_variant_playlist(self.session, hls_url)
        except BaseException:
            self.logger.error("The requested channel is unavailable.")


__plugin__ = WebcastIndiaGov
