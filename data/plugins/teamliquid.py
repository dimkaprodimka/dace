#-plugin-sig:ND2/VVxgC50uZtOmrLOgqDPVuns9uAIqX4SFTu3n3tE8wbokN3XMd+E/svXj5NTadwbv4fWqHhr8ZcXJHeNWqAhMJkW2mNjhYyFucjl2cH+G8bx7vzEe0xpMML9VyM9YXYSWG5QOCVGY480INGBwNJ4TZkIHcVyfm6m5Sa0L+Eq7YrL1nkvmDASWXTwPlsjwjXA1IfXi/4/YRNWRQPZlY4u2/wQbLa3nSMGGA6AVMahCFfKYHbNMubBGNfLQkA3Pitj6PgGAuanvvhSVzBZX5wpywjCjCv/ABDmaNIfZMNwOiwkoBzfJuZqfGRL3KayC80n0L2UXv02fr+JopMzlIg==
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import urlparse
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api.support_plugin import afreeca
from ACEStream.PluginsContainer.streamlink.plugin.api.support_plugin import twitch

AfreecaTV = afreeca.AfreecaTV
Twitch = twitch.Twitch

log = logging.getLogger(__name__)


class Teamliquid(Plugin):
    _url_re = re.compile(r'''https?://(?:www\.)?(?:tl|teamliquid)\.net/video/streams/''')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)

        stream_address_re = re.compile(r'''href\s*=\s*"([^"]+)"\s*>\s*View on''')

        stream_url_match = stream_address_re.search(res.text)
        if stream_url_match:
            stream_url = stream_url_match.group(1)
            log.info("Attempting to play streams from {0}".format(stream_url))
            p = urlparse(stream_url)
            if p.netloc.endswith("afreecatv.com"):
                self.stream_weight = AfreecaTV.stream_weight
            elif p.netloc.endswith("twitch.tv"):
                self.stream_weight = Twitch.stream_weight
            return self.session.streams(stream_url)


__plugin__ = Teamliquid
