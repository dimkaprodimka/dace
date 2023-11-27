#-plugin-sig:BzCNm+I5xZdPpYgioHevFvR83YgZUPhvtmbCrl0AuUTc075TiVurXhIE1CVJKdU6hSj/Iufe+89IB/bmcLIrOqyq4AazU3QREa6tArR424SIhj5GRdwdW5/yq6o+weMku//4KDFM7QuH2TpKOIdUzMSmYuOUnE0di57z8VvNwUedxwZJGp/EILZYxxhozy9jMS4WwqJ7hDv1KHm7HeivMJA1NwrsEHR6kuLjjV7qlqo/Gas6pHst+iP9VTrmIsM8zxoEOkOeJ9YmJl/ISOtX1xUgfn6gfqkJZa8vyGvqMAKLKrbfxADovh7Y8qR6JJr53CltVpgX61yEaXk+ZjDx9A==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class Sportal(Plugin):

    _url_re = re.compile(
        r'https?://(?:www\.)?sportal\.bg/sportal_live_tv.php.*')
    _hls_re = re.compile(r'''["'](?P<url>[^"']+\.m3u8[^"']*?)["']''')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        self.session.http.headers.update({'User-Agent': useragents.FIREFOX})
        res = self.session.http.get(self.url)
        m = self._hls_re.search(res.text)
        if not m:
            return

        hls_url = m.group('url')
        log.debug('URL={0}'.format(hls_url))
        log.warning('SSL certificate verification is disabled.')
        return HLSStream.parse_variant_playlist(
            self.session, hls_url, verify=False).items()


__plugin__ = Sportal
