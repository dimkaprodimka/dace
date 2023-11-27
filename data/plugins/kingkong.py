#-plugin-sig:X317YRwZgsNarreG4pvMJWz9JyWHFrIQdtQfmcy1l2PlrGalkxZ2Us5s4ZAsNTVNyvxSwSshkKsw4CBnCMez29H0d2Q0M6itO0xFxT30YmOa2T6e3yD7Dby8oeT8XQF7GOQLyffvR4lwJGZ88M5tkTO+kXNrsrCHIS089bo1LD+2zGmrA4jZwDmMGuTOraFxz+Y/z25KenMYPfVbJWDoI+ARntflN8FJ/lJvLfGCqeIq/4E7n/+zk6OIeKfJdluHn9beEF0GF7JjR/8TauPKMISx/m03pRFEv5n4LkmDRJcZ2nkXrfFvy5aRXZI0o4FmNp8KB4UivIaahkkt6Tya7Q==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HTTPStream, HLSStream

API_URL = "https://g-api.langlive.com/webapi/v1/room/info?room_id={0}"
VOD_API_URL = (
    "https://g-api.langlive.com/webapi/v1/replayer/detail?live_id={0}")
STATUS_ONLINE = 1
STATUS_OFFLINE = 0
STREAM_WEIGHTS = {
    "360P": 360,
    "480P": 480,
    "720P": 720,
    "source": 1080
}

_url_re = re.compile(r"""
    https://www\.kingkong\.com\.tw/
    (?:
        video/(?P<vid>[0-9]+G[0-9A-Za-z]+)|
        (?P<channel>[0-9]+)
    )
""", re.VERBOSE)

_room_schema = validate.Schema(
    {
        "data": {
            "live_info": {
                "live_status": int,
                "stream_items": [{
                    "title": validate.text,
                    "video": validate.any('', validate.url(
                        scheme="https",
                        path=validate.endswith(".flv")
                    ))
                }]
            }
        }
    },
    validate.get("data")
)

_vod_schema = validate.Schema(
    {
        "data": {
            "live_info": {
                "video": validate.text
            }
        }
    },
    validate.get("data")
)


class Kingkong(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    @classmethod
    def stream_weight(cls, stream):
        if stream in STREAM_WEIGHTS:
            return STREAM_WEIGHTS[stream], "kingkong"
        return Plugin.stream_weight(stream)

    def _get_streams(self):
        match = _url_re.match(self.url)
        vid = match.group("vid")

        if vid:
            res = self.session.http.get(VOD_API_URL.format(vid))
            data = self.session.http.json(res, schema=_vod_schema)
            yield "source", HLSStream(
                self.session, data["live_info"]["video"])
            return

        channel = match.group("channel")
        res = self.session.http.get(API_URL.format(channel))
        room = self.session.http.json(res, schema=_room_schema)
        if not room:
            self.logger.info("Not a valid room url.")
            return

        live_info = room["live_info"]
        if live_info["live_status"] != STATUS_ONLINE:
            self.logger.info("Stream currently unavailable.")
            return

        for item in live_info["stream_items"]:
            quality = item["title"]
            if quality == u"\u6700\u4f73":  # "Best" in Chinese
                quality = "source"
            yield quality, HTTPStream(self.session, item["video"])


__plugin__ = Kingkong
