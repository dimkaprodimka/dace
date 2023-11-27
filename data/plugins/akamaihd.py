#-plugin-sig:DQweU/E6Z+JB/A2SSAAkFMS8Oj4DbmUFEOcgD72k2LBsIkBsLb9uySY1i2RLskrXeGBY7smhq5qNJ3MWT0McYs6MIS28GQmZGHWqJFOS5i41nnIDETSp5UszCji6ZwQYDZaUvrXh9keDrBu+sH3RirbsUcLWGZV1qsr9gcRX/29MNU0Qe4UOVOeUUNTorLrxX6t5Tp0dnU3bA1DlXvfnOulEOKlPOEz4G6g8BZEQDfRAchPLg0aZ/7YtMT6B1S7BRbQ7mFyfapGFY0E26twgMv5F47KLsSVosw9fhbOEeOzeBk0vhRvbxo+Xrqte1DO7mi8qlh3bwaITEq2E5vLISg==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.plugin import parse_url_params
from ACEStream.PluginsContainer.streamlink.stream import AkamaiHDStream
from ACEStream.PluginsContainer.streamlink.utils import update_scheme


class AkamaiHDPlugin(Plugin):
    _url_re = re.compile(r"akamaihd://(.+)")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        url, params = parse_url_params(self.url)
        urlnoproto = self._url_re.match(url).group(1)
        urlnoproto = update_scheme("http://", urlnoproto)

        self.logger.debug("URL={0}; params={1}", urlnoproto, params)
        return {"live": AkamaiHDStream(self.session, urlnoproto, **params)}


__plugin__ = AkamaiHDPlugin
