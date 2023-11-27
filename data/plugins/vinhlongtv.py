#-plugin-sig:ZRDBcEfDxehr/q3OCAdKS4BXsbsCJYr+FDI+BZYT0tb+NyQUydTb+C/ec+c/91ENifyZ3YOsl3o+lzaAcIA4RhVztTZj79lTWV1Js0U+j1u4Bk0a3bpRBmxfw+VXciKgTWitWnUVf1nS1gwdtyQnx0uxDLpi9SQr+Cfz/wrHraBF3Ghc8USJ7Wck+ZWDSn4hGKNQ5oUD8+BvuJTUC7jehUwDnZQz+O0Q+UOaCYrh6JF6mPZqVSE3wZiM4BE4FoB8KRQj3Pq/ZIvvZFnCYFNVL8HQ4szsrqQqHyMNv831t3M3Msyrf9ijnYS006hOHwAUNqSJq7Oz9SzoGcvd/Ixd2g==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents, validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class VinhLongTV(Plugin):

    api_url = 'http://api.thvli.vn/backend/cm/detail/{0}/'

    _url_re = re.compile(
        r'https?://(?:www\.)?thvli\.vn/live/(?P<channel>[^/]+)')

    _data_schema = validate.Schema(
        {
            'link_play': validate.text,
        },
        validate.get('link_play')
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        self.session.http.headers.update({'User-Agent': useragents.FIREFOX})

        channel = self._url_re.match(self.url).group('channel')

        res = self.session.http.get(self.api_url.format(channel))
        hls_url = self.session.http.json(res, schema=self._data_schema)
        log.debug('URL={0}'.format(hls_url))

        streams = HLSStream.parse_variant_playlist(self.session, hls_url)
        if not streams:
            return {'live': HLSStream(self.session, hls_url)}
        else:
            return streams


__plugin__ = VinhLongTV
