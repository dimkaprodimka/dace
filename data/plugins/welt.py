#-plugin-sig:MbROpo6E2JbIusJKgXVSYr8EDysscGyQMse/vtupHSH+UyMEM8256M+mUf3d5ACT0bWI1FH2yDltE+AIr3dCPnqd/yLgavwUVxQLC2hSLifucVsOQ/guTCfqDWm58XpWc9DOq1lY6JYCsMF40AmtnMxYDBY0ONmoGfYVbMNuCmNykdFkJX58RWoB9hRzO6I/BM0Ch56iPzG9WdZrCH8+wBamgAM2oSIJs9RhamBazLR9DRiwoIQ1I0f3s0nAZSUIKp9DUzPt6J/9fr9l2RNHCtlkQaTGRbwQ4HKdfvU8VGHz8RHwrcjyz6+tXhfwnX0cAFa4iHxU3KCaZC/jWI+9mw==
import re

from ACEStream.PluginsContainer.streamlink.compat import quote
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents, validate
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import itertags
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json


def get_json(text):
    for script in itertags(text, "script"):
        if script.attributes.get("type") == "application/json" \
                and script.attributes.get("data-content") == "VideoPlayer.Config":
            return script.text
    return None


class Welt(Plugin):
    _re_url = re.compile(
        r"""https?://(\w+\.)?welt\.de/?""",
        re.IGNORECASE
    )
    _re_url_vod = re.compile(
        r"""mediathek""",
        re.IGNORECASE
    )
    _url_vod = "https://www.welt.de/onward/video/play/{0}"
    _schema = validate.Schema(
        validate.transform(get_json),
        validate.transform(parse_json),
        validate.get("sources"),
        validate.filter(lambda obj: obj["extension"] == "m3u8"),
        validate.map(lambda obj: obj["src"]),
        validate.get(0)
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._re_url.match(url) is not None

    def __init__(self, url):
        Plugin.__init__(self, url)
        self.url = url
        self.isVod = self._re_url_vod.search(url) is not None

    def _get_streams(self):
        headers = {"User-Agent": useragents.CHROME}
        hls_url = self.session.http.get(self.url, headers=headers, schema=self._schema)
        headers["Referer"] = self.url

        if self.isVod:
            url = self._url_vod.format(quote(hls_url, safe=""))
            hls_url = self.session.http.get(url, headers=headers).url

        return HLSStream.parse_variant_playlist(self.session, hls_url, headers=headers)


__plugin__ = Welt
