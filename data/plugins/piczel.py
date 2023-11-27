#-plugin-sig:nlz6VgodLuZ/0lSLE0tVm4e1v8s7cvv7aBHdZXM68dTmWGS78l642Hg60LudqmeCrtSz2ysnTaWDISYDHZ8+EWebsA04EgVoaIf7LdJZfbV37SeZZEDPNk4XxxYp3/HvwKtDAcuymKd4HE9R09n2oPZD2YEj9BCTA80830ULtRvND80dGcIK6UvsUSFWoBuqlxY6O7T3K5yU5YRu598fm4ZqInzFJd2oFyDg0b+Nafbk3vXD6wh3flFAd04FQzVH5NKf2uXwgiZLcLZG02NV8saspqPcmBQUlTopxCALPCrZl303troJZGy8I7dPfWl2b5Lxd4dHHxYTEx4Uw+uJxA==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


STREAMS_URL = "https://piczel.tv/api/streams?followedStreams=false&live_only=false&sfw=false"
HLS_URL = "https://piczel.tv/hls/{0}/index.m3u8"

_url_re = re.compile(r"https://piczel.tv/watch/(\w+)")

_streams_schema = validate.Schema([
    {
        "id": int,
        "live": bool,
        "slug": validate.text
    }
])


class Piczel(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        if not match:
            return

        channel_name = match.group(1)

        res = self.session.http.get(STREAMS_URL)
        streams = self.session.http.json(res, schema=_streams_schema)

        for stream in streams:
            if stream["slug"] != channel_name:
                continue

            if not stream["live"]:
                return

            log.debug("HLS stream URL: {}", HLS_URL.format(stream["id"]))

            return {"live": HLSStream(self.session, HLS_URL.format(stream["id"]))}


__plugin__ = Piczel
