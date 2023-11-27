#-plugin-sig:I7A6gDskD9wsTSdl62KL+EBaprZNt7iPU2mCnfHATHfPsYMaED1o1TYSOIFeYqtgCKhI/DuSYuNd36hHzLCNWtvpwCi6hi31ij/XlsaKPxlH0NfprjfTM1BNBZhk3/dVAN8oFq9xcBEpP207nBqD94IqCdBcawztIsrQsRwNLrxnLr0OfEzBt45uoi1jlZoq5uerlcPOMqyngy0IkqZrAcjKMgwURODgiERLzRRrA1RC2NaXd11lQINgJoKA3l1KWYJiJaVD6EvcbIm1bqL0JUs35OmtVta6rmjDtZiZrN8FVij89PMHS4jC6GafqSWyqp/nFViJPMlPDQX1VVqL3Q==
from __future__ import print_function
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class FoxTR(Plugin):
    """
    Support for Turkish Fox live stream: http://www.fox.com.tr/canli-yayin
    """

    url_re = re.compile(r"""
        https?://(?:www.)?
        (?:fox.com.tr/.*|
           foxplay.com.tr/.*)
    """, re.VERBOSE)

    playervars_re = re.compile(r"source\s*:\s*\[\s*\{\s*videoSrc\s*:\s*(?:mobilecheck\(\)\s*\?\s*)?'([^']+)'")

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        match = self.playervars_re.search(res.text)
        if match:
            stream_url = match.group(1)
            return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = FoxTR
