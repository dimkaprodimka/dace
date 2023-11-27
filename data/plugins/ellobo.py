#-plugin-sig:g3Guv2ClUPLypt9k3raAnNVXTR/vLai4egCz46GcHfm3wAApw578Bhh5TwN8NJfsXdHyvn8I1Ni5KpJy5TgkZR78jc+zx6aEES4ZiPijwnukkPLg3FN9fSjFHZG1qeHDqGFkgsLP+kPoEgYvwvcjjJFwf2B4yW7urFqM+gNrjFkXWHFbKChAzPrcu0n4cI1kFTlnjoMY72SXG8iCWWDn+vJGS2wAx7hAhGvVeIJpl3FWptnkjeF6Q2IOp36/haXoi/B5K1/QhuLUIA5TnLokW78biKGM6LKHrY8AuQCyxX5pkMo9w1y4gX0wK6B8w6IpOW96LXByT7MScg7qr0O9cQ==
import re

from ACEStream.PluginsContainer.streamlink import NoPluginError
from ACEStream.PluginsContainer.streamlink import PluginError
from ACEStream.PluginsContainer.streamlink.plugin import Plugin


class ElLobo(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?ellobo106\.com/")
    iframe_re = re.compile(r'<iframe.*?src="([^"]+)".*?>.*?</iframe>', re.DOTALL)

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        # Search for the iframe in the page
        iframe_m = self.iframe_re.search(res.text)

        ustream_url = iframe_m and iframe_m.group(1)
        if ustream_url and "ott.streann.com" in ustream_url:
            try:
                return self.session.streams(ustream_url)
            except NoPluginError:
                raise PluginError("Could not play embedded stream: {0}".format(ustream_url))


__plugin__ = ElLobo
