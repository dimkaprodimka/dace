# -*- coding: utf-8 -*-
#-plugin-sig:dQAM4wnZg3EvNOcr6IOYf3CtdpfWQVBlPf/GzQWG1GQYMcUUT4uqDuWcBl0Sdqhte4doZ4715XDspn+I6rvMIMtJz3Uv9ijTTLe7gC8TCE2RmglaAwNehs4RRjFNG6FnR+vz3F72O1FURS9kzdeNl9HTXVydvpoiQPwbEpS1xNcmQh0hN9YY805Ultz3KaH0hNxzJoj6OwFTim2ZFkR4oUM1E5r15lk8T0aInFD3/GiFTmbBqt4g55MiEvEZA6duRAJ7e05deVonqtvLkb8zIoUapzAXjJ7yu9JM3DQFh/DbVX+77Y5ixeJpg/LVO6l2FwG9qU0VoGN+cY1MbeYwhA==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream, HTTPStream, RTMPStream

CHANNEL_INFO_URL = "http://api.plu.cn/tga/streams/%s"
QQ_STREAM_INFO_URL = "http://info.zb.qq.com/?cnlid=%d&cmd=2&stream=%d&system=1&sdtfrom=113"
PLU_STREAM_INFO_URL = "http://livestream.plu.cn/live/getlivePlayurl?roomId=%d"
_quality_re = re.compile(r"\d+x(\d+)$")
_url_re = re.compile(r"http://(star|y)\.longzhu\.(?:tv|com)/(m\/)?(?P<domain>[a-z0-9]+)")

_channel_schema = validate.Schema(
    {
        "data": validate.any(None, {
            "channel": validate.any(None, {
                "id": int,
                "vid": int
            })
        })
    },
    validate.get("data")
)

_plu_schema = validate.Schema(
    {
        "playLines": [{
            "urls": [{
                "securityUrl": validate.url(scheme=validate.any("rtmp", "http")),
                "resolution": validate.text,
                "ext": validate.text
            }]
        }]
    }
)

_qq_schema = validate.Schema(
    {
        validate.optional("playurl"): validate.url(scheme="http")
    },
    validate.get("playurl")
)

STREAM_WEIGHTS = {
    "middle": 540,
    "source": 1080
}


class Tga(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    @classmethod
    def stream_weight(cls, stream):
        if stream in STREAM_WEIGHTS:
            return STREAM_WEIGHTS[stream], "tga"

        return Plugin.stream_weight(stream)

    def _get_quality(self, label):
        match = _quality_re.search(label)
        if match:
            return match.group(1) + "p"
        else:
            return "live"

    def _get_channel_id(self, domain):
        channel_info = self.session.http.get(CHANNEL_INFO_URL % str(domain))
        info = self.session.http.json(channel_info, schema=_channel_schema)
        if info is None:
            return 0, 0

        return info['channel']['vid'], info['channel']['id']

    def _get_qq_streams(self, vid):
        res = self.session.http.get(QQ_STREAM_INFO_URL % (vid, 1))
        info = self.session.http.json(res, schema=_qq_schema)
        yield "live", HTTPStream(self.session, info)

        res = self.session.http.get(QQ_STREAM_INFO_URL % (vid, 2))
        info = self.session.http.json(res, schema=_qq_schema)
        yield "live", HLSStream(self.session, info)

    def _get_plu_streams(self, cid):
        res = self.session.http.get(PLU_STREAM_INFO_URL % cid)
        info = self.session.http.json(res, schema=_plu_schema)
        for source in info["playLines"][0]["urls"]:
            quality = self._get_quality(source["resolution"])
            if source["ext"] == "m3u8":
                yield quality, HLSStream(self.session, source["securityUrl"])
            elif source["ext"] == "flv":
                yield quality, HTTPStream(self.session, source["securityUrl"])
            elif source["ext"] == "rtmp":
                yield quality, RTMPStream(self.session, {
                    "rtmp": source["securityUrl"],
                    "live": True
                })

    def _get_streams(self):
        match = _url_re.match(self.url)
        domain = match.group('domain')

        vid, cid = self._get_channel_id(domain)

        if vid != 0:
            return self._get_qq_streams(vid)
        elif cid != 0:
            return self._get_plu_streams(cid)


__plugin__ = Tga
