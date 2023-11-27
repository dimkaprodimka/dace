#-plugin-sig:iPScvi1h37inWf4ax0qip+6t0bxcOieYuV342jFRG5jZYrlFgszkP8Q4WwsOpvE8w+MbzDVUHuDnrOVYVMcowtW9srIkuu3C5sJrwYlAmRBqMfK3jVSxx2ITf71MaDViqKLfsGE0lDUyWZKzWGI77E0phggRwNV3lZA4HD9l8rQH9be5Xq5pvuWtTmcp124gHBAazI+mMcP5o1li5TXQCnrwWhr7ufKT8gvl6lEUy4jMfuMSq2mikkAXx+FytCOuO+i1spiNPpmhPtsc4EG/NI59ZEMfkvDLU4bUFc49biwMGYbmGTjavHApaTTO9cunyViP1beWgdM1AoevxYWKng==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents, validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class Bigo(Plugin):
    _url_re = re.compile(r"https?://(?:www\.)?bigo\.tv/([^/]+)$")
    _api_url = "https://www.bigo.tv/OInterface/getVideoParam?bigoId={0}"

    _video_info_schema = validate.Schema({
        "code": 0,
        "msg": "success",
        "data": {
            "videoSrc": validate.any(None, "", validate.url())
        }
    })

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        match = self._url_re.match(self.url)
        res = self.session.http.get(
            self._api_url.format(match.group(1)),
            allow_redirects=True,
            headers={"User-Agent": useragents.IPHONE_6}
        )
        data = self.session.http.json(res, schema=self._video_info_schema)
        videourl = data["data"]["videoSrc"]
        if videourl:
            yield "live", HLSStream(self.session, videourl)


__plugin__ = Bigo
