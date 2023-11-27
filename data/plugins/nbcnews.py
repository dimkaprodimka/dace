#-plugin-sig:f4ZjfpsZUmhyrkgdPNUvIuhl+8pHdjB+qf3Ujfd1wS3vqil0EMK6dAm9+/EpxsqgaFrj5tqjI3Q8zEhw0zrzPs1r2ppgK+1UH+H9V9hms7xDvx6A2pN0voU0C/CeinDY6Faa/Aa6Dz8ArkCNVWYy21vDv59JTobuQyYOQsUztBEbKETGbRAifLVHjB2bupQr812aeTpfA1a3rlK8CfcEMD4NVFehQYfM2JodMFVIBEu4aguT8LZoYkUxRmb9x2cX/hhnnsLQ+PllbdFLQYnxlX1Ej+VE3UMP/QM8+Po6mhSxlrh0GKiyVnjfGGipBQ4DIar4zIa51ZNtO+KgqYI76Q==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json

log = logging.getLogger(__name__)


class NBCNews(Plugin):
    url_re = re.compile(r'https?://(?:www\.)?nbcnews\.com/now')
    js_re = re.compile(r'https://ndassets\.s-nbcnews\.com/main-[0-9a-f]{20}\.js')
    api_re = re.compile(r'NEWS_NOW_PID="([0-9]+)"')
    api_url = 'https://stream.nbcnews.com/data/live_sources_{0}.json'
    api_schema = validate.Schema(validate.transform(parse_json), {
        'videoSources': [{
            'sourceUrl': validate.url(),
            'type': validate.text
        }]
    }, validate.get('videoSources'), validate.get(0))

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def get_title(self):
        return 'NBC News Now'

    def _get_streams(self):
        html = self.session.http.get(self.url).text
        match = self.js_re.search(html)
        js = self.session.http.get(match.group(0)).text
        match = self.api_re.search(js)
        log.debug('API ID: {0}'.format(match.group(1)))
        api_url = self.api_url.format(match.group(1))
        stream = self.session.http.get(api_url, schema=self.api_schema)
        log.trace('{0!r}'.format(stream))
        if stream['type'].lower() != 'live':
            log.error('invalid stream type "{0}"'.format(stream['type']))
            return
        return HLSStream.parse_variant_playlist(self.session, stream['sourceUrl'])


__plugin__ = NBCNews
