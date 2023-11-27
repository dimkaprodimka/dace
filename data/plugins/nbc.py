#-plugin-sig:KgtIJACNGzXgQ2gioIAcpBJHTaA5XLBF9oSgc9MXwl0FQDOsvHsOzP/JUoH4CBA1HL14HvU+82kuqR7IQjmp/xMvo8IXXgQlk3rdV475CXmi1nLln5qkWs0CrAQM0MCLZlLW8HIiHz5hwDi+Z0qpVFyTJDp1s3P5IQIRo/TFcSXX7UEXNY4TOnCZB0Zy3ZJLI5XZJX0F3QegjTnRE5KmYkVb2qceRuBKy73EjKy/h29zetIG4JXPqaAaW0Wl2jdYB8B7iQAoEZoys4REmr89hNNgKGFHxDSLj8tdgAq2y3X3cpNjK4rDp13cjvsURuFrQDxjxmqs/1L8ofNKcCFfmg==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api.support_plugin import theplatform
from ACEStream.PluginsContainer.streamlink.utils import update_scheme

ThePlatform = theplatform.ThePlatform

class NBC(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?nbc\.com")
    embed_url_re = re.compile(r'''(?P<q>["'])embedURL(?P=q)\s*:\s*(?P<q2>["'])(?P<url>.*?)(?P=q2)''')

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        m = self.embed_url_re.search(res.text)
        platform_url = m and m.group("url")

        if platform_url:
            url = update_scheme(self.url, platform_url)
            # hand off to ThePlatform plugin
            p = ThePlatform(url)
            p.bind(self.session, "plugin.nbc")
            return p.streams()


__plugin__ = NBC
