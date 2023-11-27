#-plugin-sig:oUmlgv0hH5Is61b3OoJ/bQWEWzyTtN+8NJWpWInsvYplWmqrH/FOV2XWO1TXsTcHfsWpnYe0zFPkchLl0D1VCT32psnKheyGzhKYvjvQ/MWhd3VtJJrBFacZDaSaR4257oqNdkrlbu5NjFj/qJfzZdv2Ccrp4rO7dAIlfhJFnpvkaSkQxYlJK9R7TrtZnADxyEbEUDFR3KbnOcuFkTwOtx5cWjspxEy4foMpBQxTXfRGypCe5njczfA7qjWbAhKQnbmNoABZtG8SasZziyCfdV7xmu+9z6BbRI+Q9WAV8wK3jz2y+gaPKrbtIMf8sO3xL2Ar8oWSHdVeZief5AacEg==
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import urlparse
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import itertags
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class LtvLsmLv(Plugin):
    """
    Support for Latvian live channels streams on ltv.lsm.lv
    """
    url_re = re.compile(r"https?://ltv\.lsm\.lv/lv/tieshraide")

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        self.session.http.headers.update({
            "Referer": self.url,
            "User-Agent": useragents.FIREFOX
        })

        iframe_url = None
        res = self.session.http.get(self.url)
        for iframe in itertags(res.text, "iframe"):
            if "embed.lsm.lv" in iframe.attributes.get("src"):
                iframe_url = iframe.attributes.get("src")
                break

        if not iframe_url:
            log.error("Could not find player iframe")
            return

        log.debug("Found iframe: {0}".format(iframe_url))
        res = self.session.http.get(iframe_url)
        for source in itertags(res.text, "source"):
            if source.attributes.get("src"):
                stream_url = source.attributes.get("src")
                url_path = urlparse(stream_url).path
                if url_path.endswith(".m3u8"):
                    for s in HLSStream.parse_variant_playlist(self.session,
                                                              stream_url).items():
                        yield s
                else:
                    log.debug("Not used URL path: {0}".format(url_path))


__plugin__ = LtvLsmLv
