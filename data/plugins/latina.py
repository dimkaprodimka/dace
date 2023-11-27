#-plugin-sig:FzwxPiwfeXoEfHRjKVk5cAW48QiTmXX8CoyYuvaEVZBpZcpW553BFpfsCDWy7NmVY0Adp+7luscEUIDK/jJQY/Ig4MEzPf2T2THc858utAMKxTv/93tP3mI+kB56MBcm3eb9lTD5EZN9EGjhVkaUwgUEcaq2Qu5iqEgK9avSxG+a8T0dESBHxMAR1rDLKOHLWEbu7LZR/V5eBKKBiEWWnugWfZp7D0Ej8aSIinUx3Li7Y9Wd2huOigob7vfr+WfXqpyZiC4AjZv6Uln7mLiN9LPUvJkOpWYoyGEmjuO8VYWxPNUDckYWg7JY9HkAQIWg+MWRl5Syvwjw3/TyIUKcLA==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import itertags
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class Latina(Plugin):
    _url_re = re.compile(r"https?://(?:www\.)?latina\.pe/tvenvivo")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def get_title(self):
        return "Latina"

    def _get_streams(self):
        self.session.http.headers.update({
            "User-Agent": useragents.CHROME,
            "Referer": self.url})

        self.session.http.get(self.url)
        stream_url = None
        for div in itertags(self.session.http.get(self.url).text, "div"):
            if div.attributes.get("id") == "player":
                stream_url = div.attributes.get("data-stream")

        if stream_url:
            log.debug("URL={0}".format(stream_url))
            return HLSStream.parse_variant_playlist(self.session,
                                                    stream_url,
                                                    name_fmt="{pixels}_{bitrate}")


__plugin__ = Latina
