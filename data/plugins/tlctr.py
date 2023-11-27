#-plugin-sig:RLNgU9Oa7//E94FN6NwA00KN5E3cLxSfExQlgojyKliXx8m853dDb4HYMJA+MnPQAQsKaDQbaLy/1Z2oh9igzT4c0FHEcqZl0C4186Kh0m15R3z9zXYy6xU6T2pi6eRC/LbG21JoE6KYwXShr6zwC9fuRnnP/HZAb+2+rRUZWDC3dwUw4hF7f9CYX/GqK5/fhMqsDLeH1tz6FYiPw19ETyET3s/Q8FAbUE/SV+3Dd3FrIBxZ41WFZ66qLglq9a8x368cN0764ghj+EBhQluBvUH7hHVEF5XCOlS5Pzu/RgQYMNdgnQZu+Pn27bDruuZ83vfz06t9JZo+u7068ov0Yw==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class TLCtr(Plugin):

    _url_re = re.compile(r'https?://(?:www\.)?tlctv\.com\.tr/canli-izle')
    _hls_re = re.compile(
        r'''["'](?P<url>https?://[^/]+/live/hls/[^"']+)["']''')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        self.session.http.headers.update({'User-Agent': useragents.FIREFOX})
        res = self.session.http.get(self.url)

        m = self._hls_re.search(res.text)
        if not m:
            log.error('No playlist found.')
            return

        hls_url = m.group('url')
        log.debug('URL={0}'.format(hls_url))
        streams = HLSStream.parse_variant_playlist(self.session, hls_url)
        if not streams:
            return {'live': HLSStream(self.session, hls_url)}
        else:
            return streams


__plugin__ = TLCtr
