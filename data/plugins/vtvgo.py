#-plugin-sig:UdWgbP2dJAwVgZq8dMjWQTby6amBOoF8hgSakuNzxAnfkXHdl0HnfLJnchphtE9ELbYeK0Nyqu9WvzvbvfpKyV2yO2V8uRaGe2OQY4FSqqNYs9V2w4TM0//0Adlui96qkS4QIrvhuvKhsvo/zH6+ZpZHc1nixpcY49Le5ztqQfpXhsb9/pdJVL/8FfBeikHy0duknHRE80E1I/TDqpp+GhjaZtyCUcInR2JOgxW+wczTc0ZSOi8eK0oQ0FpSpej32OKLg/fFvSA4PVce7/uc5cpOMGTouLmIqH8kuwS+Xz9Da9h9vgvl2piu40olhtKKucT1laD1zy9UKc/ozDVbFw==
import logging
import re

from ACEStream.PluginsContainer.streamlink.exceptions import PluginError
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class VTVgo(Plugin):

    AJAX_URL = 'https://vtvgo.vn/ajax-get-stream'

    _url_re = re.compile(r'https://vtvgo\.vn/xem-truc-tuyen-kenh-')
    _params_re = re.compile(r'''var\s(?P<key>(?:type_)?id|time|token)\s*=\s*["']?(?P<value>[^"']+)["']?;''')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        self.session.http.headers.update({
            'Origin': 'https://vtvgo.vn',
            'Referer': self.url,
            'User-Agent': useragents.FIREFOX,
            'X-Requested-With': 'XMLHttpRequest',
        })
        res = self.session.http.get(self.url)

        params = self._params_re.findall(res.text)
        if not params:
            raise PluginError('No POST data')
        elif len(params) != 4:
            raise PluginError('Not enough POST data: {0!r}'.format(params))

        log.trace('{0!r}'.format(params))
        res = self.session.http.post(self.AJAX_URL, data=dict(params))
        hls_url = self.session.http.json(res)['stream_url'][0]

        return HLSStream.parse_variant_playlist(self.session, hls_url)


__plugin__ = VTVgo
