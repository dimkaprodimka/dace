#-plugin-sig:Hxdm5IFeQHFvrPagy4wOrLM4zM04F9QHM7nLFgdTy5b7vsc7x1K2hl5TFHKB8Ah/zV0OdTsqk/7r45iPUbdzL3K1S/pe7DP0U7j94FyEsUNb6aTDGJKjCBR4fdBP8bIyCmJHQgcbvuMYuc4xsxeERaHQhU6wz6Uu5Wi0N4M5i0Zild2WHMQkbiJ+KRwz0df4UDccrzv9WsPKHWvsyzRhLdiVk1ofp8XQAUh0K90sK2HuCxTxaW0GgSWIBl/sKhSdibESuWzJbCaUFOETW+3LZWqE3ZUQuiBmZ38P9jfAyuqxsd82Qq4JtoOkFzJy1l7gSq5lmvW/kdAJagbos5kRJQ==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents, validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream, RTMPStream, HTTPStream

log = logging.getLogger(__name__)


class App17(Plugin):
    _url_re = re.compile(r"https://17.live/live/(?P<channel>[^/&?]+)")
    API_URL = "https://api-dsa.17app.co/api/v1/lives/{0}/viewers/alive"

    _api_schema = validate.Schema(
        {
            "rtmpUrls": [{
                validate.optional("provider"): validate.any(int, None),
                "url": validate.url(),
            }],
        },
        validate.get("rtmpUrls"),
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        match = self._url_re.match(self.url)
        channel = match.group("channel")

        self.session.http.headers.update({'User-Agent': useragents.CHROME, 'Referer': self.url})

        data = '{"liveStreamID":"%s"}' % (channel)

        try:
            res = self.session.http.post(self.API_URL.format(channel), data=data)
            res_json = self.session.http.json(res, schema=self._api_schema)
            log.trace("{0!r}".format(res_json))
            http_url = res_json[0]["url"]
        except Exception as e:
            log.info("Stream currently unavailable.")
            log.debug(str(e))
            return

        https_url = http_url.replace("http:", "https:")
        yield "live", HTTPStream(self.session, https_url)

        if 'pull-rtmp' in http_url:
            rtmp_url = http_url.replace("http:", "rtmp:").replace(".flv", "")
            stream = RTMPStream(self.session, {
                "rtmp": rtmp_url,
                "live": True,
                "pageUrl": self.url,
            })
            yield "live", stream

        if 'wansu-' in http_url:
            hls_url = http_url.replace(".flv", "/playlist.m3u8")
        else:
            hls_url = http_url.replace("live-hdl", "live-hls").replace(".flv", ".m3u8")

        s = HLSStream.parse_variant_playlist(self.session, hls_url)
        if not s:
            yield "live", HLSStream(self.session, hls_url)
        else:
            if len(s) == 1:
                for _n, _s in s.items():
                    yield "live", _s
            else:
                for _s in s.items():
                    yield _s


__plugin__ = App17
