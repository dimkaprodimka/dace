#-plugin-sig:WvdYgmLQLEJlcxgpiGwU/VT0OgoXb2FB+7uyLO5K3k5r98nn9gMzhNMhJfdGYO1NqR9q4KnMpcNRfSsnsEyeKqiDkJQiKD7e1l+Ggrt1zkVVh0d7CbIiIY09S8qJxupGbd9hhZOV1AFJelFM1tOa04ebU49xO7a1vuPXbEUB5dEv5l/5SmJvHdUUQ0ceWUVXoZIxBO21JO32qFblO3V7STu/ekjS8HJ8bvKSzjGhzSH17Rc5P3dGQAEfiRPaus597cgPE1VBwZf0HpCrFzh9nr4RyxP9ENLEG/cqNU4yD+HpZysf13fYWbqqSJ4k+z7UYZce85Lx2ivERiZ8wB8XMw==
"""
Plugin to support the videos from Delfi.lt

https://en.wikipedia.org/wiki/Delfi_(web_portal)
"""
import re
import logging

import itertools

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import itertags
from ACEStream.PluginsContainer.streamlink.stream import HTTPStream, HLSStream, DASHStream
from ACEStream.PluginsContainer.streamlink.utils import update_scheme

log = logging.getLogger(__name__)


class Delfi(Plugin):
    url_re = re.compile(r"https?://(?:[\w-]+\.)?delfi\.(lt|lv|ee)")
    _api = {
        "lt": "http://g2.dcdn.lt/vfe/data.php",
        "lv": "http://g.delphi.lv/vfe/data.php",
        "ee": "http://g4.nh.ee/vfe/data.php"
    }

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    @property
    def api_server(self):
        m = self.url_re.match(self.url)
        domain = m and m.group(1)
        return self._api.get(domain, "lt")  # fallback to lt

    def _get_streams_api(self, video_id):
        res = self.session.http.get(self.api_server,
                                    params=dict(video_id=video_id))
        data = self.session.http.json(res)
        if data["success"]:
            for x in itertools.chain(*data['data']['versions'].values()):
                src = update_scheme(self.url, x['src'])
                if x['type'] == "application/x-mpegurl":
                    for s in HLSStream.parse_variant_playlist(self.session, src).items():
                        yield s
                elif x['type'] == "application/dash+xml":
                    for s in DASHStream.parse_manifest(self.session, src).items():
                        yield s
                elif x['type'] == "video/mp4":
                    yield "{0}p".format(x['res']), HTTPStream(self.session, src)
        else:
            log.error("Failed to get streams: {0} ({1})".format(
                data['message'], data['code']
            ))

    def _get_streams(self):
        res = self.session.http.get(self.url)
        for div in itertags(res.text, 'div'):
            if div.attributes.get("data-provider") == "dvideo":
                video_id = div.attributes.get("data-id")
                log.debug("Found video ID: {0}".format(video_id))
                for s in self._get_streams_api(video_id):
                    yield s


__plugin__ = Delfi
