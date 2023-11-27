#-plugin-sig:O8oHyy8NnbYpfvsvtGQqFbbH4prnx4I0FTLF1XWCclJyfpTWtZJLg5fN5Ai1IXXaMgs0Iv5D4QRVtHsPV37Keq+jvg5ypIMCj13fmrWYT962xm2pSyAQlUmb0ZzmKIxVH+MYrAPdbO5LJTOsxD3eWq1Rniicc0J8PLb/SaB4zQKWCxDtECZq1kvSgZJSlPKnquzHhFwDHHmb4Ai2o69ITXoEtWGDiDTRvHaqpO/8Y8yXwhbjc6IogDLdpyTcOOh3DuK7nd4fHhsufX5BBcGKvn2zyh0M3NyigX/zeHXhdz0LHCsAzM968KNlgiCQ5anKds4q/yGnb3kG+NzESHPE6A==
from __future__ import print_function
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class PowerApp(Plugin):
    url_re = re.compile(r"https?://(?:www.)?powerapp.com.tr/tvs?/(\w+)")
    api_url = "http://api.powergroup.com.tr/Channels/{0}/?appRef=iPowerWeb&apiVersion=11"
    api_schema = validate.Schema(validate.all({
        "errorCode": 0,
        "response": {
            "channel_stream_url": validate.url()
        }
    }, validate.get("response")))

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        channel = self.url_re.match(self.url).group(1)

        res = self.session.http.get(self.api_url.format(channel))
        data = self.session.http.json(res, schema=self.api_schema)

        return HLSStream.parse_variant_playlist(self.session, data["channel_stream_url"])


__plugin__ = PowerApp
