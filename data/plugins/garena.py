#-plugin-sig:BNjkszOcbaymz6f+ck9pX3J9HT7Q9q9Kk83NmerwKgI3OwcERxPhiBxG2FS6PQtSC20+gBrDt5BJHku8UkS3yWwEyihvNlYSv3qtawHSNaXoY0Co/yzCiXKyLai72mMUeKBbwfX4q/oB+CpunCZ6rSCroob3QVvfSDpuyTPT4VayZygPHA/Lept3qn+4azCDKFWY05AjcsSOK4c5h7/cQ4rIlgaRsLRTVoAyqLR4t/s/O4KVUAOiEG0tsus0E2Ff8mbCy2yImfcgZDUwyn/hZQQNss5qvpxj66Yj/7Cg/krcskQ5rk4ZG78bwvyTPUFG85Kc4PaZ/RaIKd55hsG16Q==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

_url_re = re.compile(r"https?\:\/\/garena\.live\/(?:(?P<channel_id>\d+)|(?P<alias>\w+))")


class Garena(Plugin):
    API_INFO = "https://garena.live/api/channel_info_get"
    API_STREAM = "https://garena.live/api/channel_stream_get"

    _info_schema = validate.Schema(
        {
            "reply": validate.any({
                "channel_id": int,
            }, None),
            "result": validate.text
        }
    )
    _stream_schema = validate.Schema(
        {
            "reply": validate.any({
                "streams": [
                    {
                        "url": validate.text,
                        "resolution": int,
                        "bitrate": int,
                        "format": int
                    }
                ]
            }, None),
            "result": validate.text
        }
    )

    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _post_api(self, api, payload, schema):
        res = self.session.http.post(api, json=payload)
        data = self.session.http.json(res, schema=schema)

        if data["result"] == "success":
            post_data = data["reply"]
            return post_data

    def _get_streams(self):
        match = _url_re.match(self.url)
        if match.group("alias"):
            payload = {"alias": match.group("alias")}
            info_data = self._post_api(self.API_INFO, payload, self._info_schema)
            channel_id = info_data["channel_id"]
        elif match.group("channel_id"):
            channel_id = int(match.group("channel_id"))

        if channel_id:
            payload = {"channel_id": channel_id}
            stream_data = self._post_api(self.API_STREAM, payload, self._stream_schema)
            for stream in stream_data["streams"]:
                n = "{0}p".format(stream["resolution"])
                if stream["format"] == 3:
                    s = HLSStream(self.session, stream["url"])
                    yield n, s


__plugin__ = Garena
