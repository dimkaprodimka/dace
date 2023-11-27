#-plugin-sig:lTrp9TnM/XhSCAH3ymHjaVMq+bE8MA2Z1bsmqJERQUCLBd/H1bhhK85Md85by5m/2wE4tTT0pXz1fPVbnYtIMcbnZQ7jnnIGFqh9b/CINArt/tiGA6aLyqwO/yA/5nhJ9iyXMgpx7nrXY5j0ubkBiV3U+MJN9jFmAfJFCC/TSEEKOi52ImKRTbXoj3ouG63UPYMkNxtyq08YveFyZIqbTsXB7xzgmDI/GGmbsh239lZcATDD6bx0wNIfPodD3Z8VljrhQRmzp2wAaS4XkmSATqciqs5b++7k/WM5em9PyR2BFOP3Hy0Uf7eRX8kERu2c9zYK6q+TUxbISIyT8HISbA==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.plugin import parse_url_params, LOW_PRIORITY, NORMAL_PRIORITY, NO_PRIORITY
from ACEStream.PluginsContainer.streamlink.stream import HDSStream
from ACEStream.PluginsContainer.streamlink.utils import update_scheme
from ACEStream.PluginsContainer.streamlink.compat import urlparse


class HDSPlugin(Plugin):
    _url_re = re.compile(r"(hds://)?(.+(?:\.f4m)?.*)")

    @classmethod
    def priority(cls, url):
        """
        Returns LOW priority if the URL is not prefixed with hds:// but ends with
        .f4m and return NORMAL priority if the URL is prefixed.
        :param url: the URL to find the plugin priority for
        :return: plugin priority for the given URL
        """
        m = cls._url_re.match(url)
        if m:
            prefix, url = cls._url_re.match(url).groups()
            url_path = urlparse(url).path
            if prefix is None and url_path.endswith(".f4m"):
                return LOW_PRIORITY
            elif prefix is not None:
                return NORMAL_PRIORITY
        return NO_PRIORITY

    @classmethod
    def can_handle_url(cls, url):
        m = cls._url_re.match(url)
        if m:
            url_path = urlparse(m.group(2)).path
            return m.group(1) is not None or url_path.endswith(".f4m")

    def _get_streams(self):
        url, params = parse_url_params(self.url)

        urlnoproto = self._url_re.match(url).group(2)
        urlnoproto = update_scheme("http://", urlnoproto)

        return HDSStream.parse_manifest(self.session, urlnoproto, **params)


__plugin__ = HDSPlugin
