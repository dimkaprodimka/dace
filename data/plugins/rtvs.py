#-plugin-sig:aVO0CY/7KbbGsTOFOwfmEWUcyw7b2p3kAbau67VQtRu2v0D0ezIuy66nWx5qCoN+B9C5NGmG9rn1K/KLGnnBDd1hHHp61QJko98tm1R2XwwLdq4obc/sQtlTpyeCKjY3EhbQ5wY8MQWtVhJY12JH192lM8zrIKHaKCEvHOCLYEnkqLzazFIcFOifP/iEQSuCeP0hV6qOo/GRT4xJbk6eywpWhq8Rvql48PNm/FfiPsYatCJ09B79CXVgNR7wudd5oQyMFzgQuRdQhiXgs2OJVAWxL/lS9dBbAtz2anfcPN8rwu2qkRBSw045CWziGx3F7lnkvvmGOt90O+nVAk1q4A==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import RTMPStream, HLSStream

RUURL = "b=chrome&p=win&v=56&f=0&d=1"

_url_re = re.compile(r"https?://www.rtvs.sk/televizia/live-[\w-]+")
_playlist_url_re = re.compile(r'"playlist": "([^"]+)"')

_playlist_schema = validate.Schema(
    [
        {
            "sources": [
                validate.any(
                    {
                        "type": "dash",
                        "file": validate.url(scheme="http")
                    }, {
                        "type": "hls",
                        "file": validate.url(scheme="http")
                    }, {
                        "type": "rtmp",
                        "file": validate.text,
                        "streamer": validate.url(scheme="rtmp")
                    }
                )
            ]
        }
    ],
    validate.get(0),
    validate.get("sources")
)


class Rtvs(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        res = self.session.http.get(self.url)
        match = _playlist_url_re.search(res.text)
        if match is None:
            return

        res = self.session.http.get(match.group(1) + RUURL)
        sources = self.session.http.json(res, schema=_playlist_schema)

        streams = {}

        for source in sources:
            if source["type"] == "rtmp":
                streams["rtmp_live"] = RTMPStream(self.session, {
                    "rtmp": source["streamer"],
                    "pageUrl": self.url,
                    "live": True
                })
            elif source["type"] == "hls":
                streams.update(HLSStream.parse_variant_playlist(self.session, source["file"]))

        return streams


__plugin__ = Rtvs
