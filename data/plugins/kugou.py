# -*- coding: utf-8 -*-
#-plugin-sig:FjG8rbwBIFvFDcUnwUvlIuorL7pVC6a+0TmVSoQCTtKhwRyVN6kJwJlTYqWSJWqUlcWy0ZHm6apcDK8CHeEP88MYutG3yf4C9kIxNEMSaqtJzn+9hP5C0jty2dRLCdlzEd0iGS3jnBSgiLFzt0B3OlV3G/k0lwZUWZpY37hElvyifjAehhubD6I40tDXh6FhNkoscXZGmDqq3dHXoT2tpHvb/SquWjU2RUfHi08eiobvDXHQd3lXRDtJh8Mtxe4nAZF72qzkLogFpEEiK4HPDPTE6EJw4iJ5KrTF7e1NfZgoDd0jJeRetdGqaYm0NffclbnYqLm+giakHmWZxXzEcQ==
import logging
import re
import time

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream, HTTPStream

log = logging.getLogger(__name__)


class Kugou(Plugin):
    _url_re = re.compile(r"""https?://fanxing.kugou.com/(?P<room_id>\d+)""")
    _roomid_re = re.compile(r"roomId:\s*'(\d+)'")
    _room_stream_list_schema = validate.Schema(
        {
            "data": validate.any(None, {
                "httpflv": validate.url()
            })
        },
        validate.get("httpflv_room_stream_list_schema")
    )

    _stream_hv_schema = validate.Schema(validate.any(
        None,
        [{
            "httpshls": [validate.url()],
            "httpsflv": [validate.url()],
        }],
    ))
    _stream_data_schema = validate.Schema({
        "msg": validate.text,
        "code": int,
        "data": {
            "status": int,
            "vertical": _stream_hv_schema,
            "horizontal": _stream_hv_schema,
            "roomId": int,
        }
    })

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        m = self._roomid_re.search(res.text)
        if m:
            room_id = m.group(1)
        else:
            room_id = self._url_re.match(self.url).group("room_id")

        res = self.session.http.get(
            "https://fx2.service.kugou.com/video/pc/live/pull/v3/streamaddr",
            params={
                "ch": "fx",
                "version": "1.0",
                # 1=rtmp, 2=httpflv, 3=hls, 5=httpsflv, 6=httpshls
                "streamType": "1-2-5-6",
                "ua": "fx-flash",
                "kugouId": "0",
                "roomId": room_id,
                "_": int(time.time()),
            }
        )
        stream_data_json = self.session.http.json(res, schema=self._stream_data_schema)
        log.trace("{0!r}".format(stream_data_json))
        if stream_data_json["code"] != 0 or stream_data_json["data"]["status"] != 1:
            return

        h = stream_data_json["data"]["horizontal"]
        v = stream_data_json["data"]["vertical"]
        stream_data = h[0] if h else v[0]

        if stream_data.get("httpshls"):
            for hls_url in stream_data["httpshls"]:
                s = HLSStream.parse_variant_playlist(self.session, hls_url)
                if not s:
                    yield "live", HLSStream(self.session, hls_url)
                else:
                    for _s in s.items():
                        yield _s

        if stream_data.get("httpsflv"):
            for http_url in stream_data["httpsflv"]:
                yield "live", HTTPStream(self.session, http_url)


__plugin__ = Kugou
