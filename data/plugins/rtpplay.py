#-plugin-sig:j+ZA7+ph/ONWi2BXsjg8N0fzlgVrKgAftIOWqdgO0Lx9A5nYynuxRVqtW+tAwqhCZqH6RBFUlFE0ltgLF5BQDVq2JDm2dyFbSgbxoGACKqfSyy8W1HJdJE83WybizdrH09TkPYjuOtRcomNoZXO9A1R+M+E6c/EGK244pDzMmBavMW82rGgnAd4zvtX04eCd/cHFPYVPUN3QhwU8pOPjjxMqeASGfpHso7OPpquTwT3b47Zs32luQgVTIoLve0q5CPoGs/Jk21fEKhSBmlTGRnqpg0rG/CMi2bt07pyRSMd2WQuCgwSg5TYmZnnee6yoprRl42WrPA6Xoxe+2586wg==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class RTPPlay(Plugin):
    _url_re = re.compile(r"https?://www\.rtp\.pt/play/")
    _m3u8_re = re.compile(r"hls:(?:\s+)?(?:\'|\")(?P<url>[^\"']+)(?:\'|\")")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        self.session.http.headers.update({"User-Agent": useragents.CHROME,
                                          "Referer": self.url})
        res = self.session.http.get(self.url)
        m = self._m3u8_re.search(res.text)
        if not m:
            log.error("Could not find _m3u8_re")
            return

        hls_url = m.group("url")
        log.debug("Found URL: {0}".format(hls_url))
        streams = HLSStream.parse_variant_playlist(self.session, hls_url)
        if not streams:
            return {"live": HLSStream(self.session, hls_url)}
        else:
            return streams


__plugin__ = RTPPlay
