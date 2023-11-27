#-plugin-sig:EThn1A8RyMTsh7+r5gBcFoFC9TMmEntV/bD/exo7ENqNv3AZOV3lqod9bBS0SGnjf+CwroSEm9poQHdMLObcq2jz821iY/tGIeqA0du8uyIMS61m0j8mA1TeLszpUlObHpdfENwO4dtYSl/Dy9KpeDl8iuM65jXwwrDb5tspcFPdqk5prV5GU07LW2Z0+FzeUEBwnjjs7RDwl1wd4MLhfcN072FHreAf8Tt1K1EOTwMDiSv0ldOr5MmBTQ2n7hvlHfdXQFqcZ6AitGE9Yaf4GkZw+vay/AQ9u+ypFhXb0+E1BKE7LrdGgM0Wv7tqT1/0w/v2ouQL7Cj7jZxMc75lwQ==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate


_url_re = re.compile(r'http(s)?://www\.skai(?:tv)?.gr/.*')
_api_url = "http://www.skaitv.gr/json/live.php"
_api_res_schema = validate.Schema(validate.all(
    validate.get("now"),
    {
        "livestream": validate.url()
    },
    validate.get("livestream"))
)


class Skai(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        api_res = self.session.http.get(_api_url)
        yt_url = self.session.http.json(api_res, schema=_api_res_schema)
        if yt_url:
            return self.session.streams(yt_url)


__plugin__ = Skai
