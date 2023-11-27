#-plugin-sig:XrbbM8ZMlgFQ2JppPgJCKelaxir1eGdEhPXi5UXqY9C/SvduTHwTbpkBkKj9hI/Dm8aNt1mX0wKD+w77kFsj1btpBzz2nl2kHd7r/86WHjNomjuvidVSPvyy/avdonTx51JHqsz9eSiKms39h/pTrA9SsH/LFmXwn8f3X+eP0KZURxuuIjYU2EeRiIZwYhJu8yfblnK5n0ceB9Jtejrb5RYdgbTkvsesFs/i9U0dpMa9BZldbZz3/tD4AP1S2stBwiU34WxHisRZrCe+ihCj3RP2s/OgJQAv8Bu8EnmGJ3Mt9GDKN6JarjH8ZwoEeenFjWlv6pckJgTWWXC5oE5llw==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.utils import update_scheme

HUYA_URL = "http://m.huya.com/%s"

_url_re = re.compile(r'https?://(www\.)?huya.com/(?P<channel>[^/]+)')
_hls_re = re.compile(r'liveLineUrl\s*=\s*"(?P<url>[^"]+)"')

_hls_schema = validate.Schema(
    validate.transform(_hls_re.search),
    validate.any(None, validate.get("url")),
    validate.transform(lambda v: update_scheme("http://", v)),
    validate.url()
)


class Huya(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        channel = match.group("channel")

        self.session.http.headers.update({"User-Agent": useragents.IPAD})
        # Some problem with SSL on huya.com now, do not use https

        hls_url = self.session.http.get(HUYA_URL % channel, schema=_hls_schema)
        yield "live", HLSStream(self.session, hls_url)


__plugin__ = Huya
