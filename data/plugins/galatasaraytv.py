#-plugin-sig:iPL0H6mS/N7JyuLaQe2Vn9C8e/Psm27byVOgnYHwIV6dMjpFpD72W7/dLcoTSmwviOleoPzbiLMsJ+qdTvkPetfAedpSRYlfsTdj2li7akVI5FlO5tTmAqDfwI4s8mcDIGGrmD4t86Ixf9ALhjgVZzFcg1jVq4u0hTznq5bc5cCQQj75K74fPP/qXp9CoOTt72VH+YonMtL/5DBElRU7c/phGmqQot4rYWgh8r82fgMwUGSU4aGVBqD8BRb5Mj189h6AmX6W3OZSaIwgE2roJMTZRSjmfMBQSTMsAK7l3zRVTyjFsYXO2qviu24zQ370uUz4a4k5PNSbcx3ZodEQFg==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class GalatasarayTV(Plugin):
    url_re = re.compile(r"https?://(?:www.)?galatasaray\.com")
    playervars_re = re.compile(r"sources\s*:\s*\[\s*\{\s*type\s*:\s*\"(.*?)\",\s*src\s*:\s*\"(.*?)\"", re.DOTALL)

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def get_title(self):
        return "Galatasaray TV"

    def _get_streams(self):
        res = self.session.http.get(self.url)
        match = self.playervars_re.search(res.text)
        if match:
            stream_url = match.group(2)
            log.debug("URL={0}".format(stream_url))
            return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = GalatasarayTV
