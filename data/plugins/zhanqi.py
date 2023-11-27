#-plugin-sig:bi2hrWlChmxUDzRZ6yUGnBkblWCaUA+yLmEKj/WAEOVvHNRM3VdigHm3ZSwlPIRsWdFKf6sMp4MOQEgEVIb0q4EzWYodSqNdk97UfN/6t+rT+4ibA1oTX66rQ2racshbIYtpj6RsuICKf/dNbVX7X+g7IKm/mAXOC7dCsRMYz/it/4Tu1am89BW3tsYaUw7VrA/tqwMgnJCQ8HNOxeHFwsWI2zw4tT7Dh9xXX5NH+EJYYoEXMBEbZBAgxez7Z1It8sASuTFSZacqNQGm8b0ic9ZlFXRxdaddpLQx+aqX+2mOO2Mnd/6d4osCGBdx5/i96OL/SgVNwydZEBibtT6pJw==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HTTPStream, HLSStream

API_URL = "https://www.zhanqi.tv/api/static/v2.1/room/domain/{0}.json"

STATUS_ONLINE = 4
STATUS_OFFLINE = 0

_url_re = re.compile(r"""
    http(s)?://(www\.)?zhanqi.tv
    /(?P<channel>[^/]+)
""", re.VERBOSE)

_room_schema = validate.Schema(
    {
        "data": validate.any(None, {
            "status": validate.all(
                validate.text,
                validate.transform(int)
            ),
            "videoId": validate.text
        })
    },
    validate.get("data")
)


class Zhanqitv(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        channel = match.group("channel")

        res = self.session.http.get(API_URL.format(channel))
        room = self.session.http.json(res, schema=_room_schema)
        if not room:
            self.logger.info("Not a valid room url.")
            return

        if room["status"] != STATUS_ONLINE:
            self.logger.info("Stream currently unavailable.")
            return

        url = "http://wshdl.load.cdn.zhanqi.tv/zqlive/{room[videoId]}.flv?get_url=".format(room=room)
        stream = HTTPStream(self.session, url)
        yield "live", stream

        url = "http://dlhls.cdn.zhanqi.tv/zqlive/{room[videoId]}_1024/index.m3u8?Dnion_vsnae={room[videoId]}".format(room=room)
        stream = HLSStream(self.session, url)
        yield "live", stream


__plugin__ = Zhanqitv
