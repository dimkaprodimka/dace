#-plugin-sig:KwXrW141KDl0g/+qyQGfrHTI4ks101ElnUjeG8jI8Mp7A/8Pu8BHaYQ9ElAMgdkOsSgy+AWzl5LT3BQgKSIWvek3u/X2qpo4EP+w16UZ43zFHtCyPyi5tbJQvpLHXn0Zkftb5w3BMmkveE5sZ/RiycUc+xotnyv02Nc1uhyMh/WG2SGhWOMfXKvppGmxbJNONMMOEx5HybIKiJ3qILjF9yyPRv0GjnbzD6gfO5m2Zpe0SjrpcG8uqnRJx7T6cTZvbpBN3btQ7q1drQ0OiEWECUqYx69ygvEc0dXCNYxdKaYjJ3kYcY6fysPPOLpj2Y3E4lX6/Tov8T82unmsADJYrg==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import update_scheme

log = logging.getLogger(__name__)


class TVToya(Plugin):
    _url_re = re.compile(r"https?://tvtoya.pl/live")
    _playlist_re = re.compile(r'data-stream="([^"]+)"')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        self.session.set_option('hls-live-edge', 10)
        res = self.session.http.get(self.url)
        playlist_m = self._playlist_re.search(res.text)

        if playlist_m:
            return HLSStream.parse_variant_playlist(
                self.session,
                update_scheme(self.url, playlist_m.group(1)),
                headers={'Referer': self.url, 'User-Agent': useragents.ANDROID}
            )
        else:
            log.debug("Could not find stream data")


__plugin__ = TVToya
