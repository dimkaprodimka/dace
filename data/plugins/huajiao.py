#-plugin-sig:QBGIKWM8pUoH1LrlHrTHWz9RHO+vyMYbbBoTEEdOfIYAkoRwbcPwYDi7CFSBZjv1WfMOthLXOgmCMCV4dwnARWbVJpOjcInMCAThVpkUsj0ktYi0vVeBlc855XylVa/2Nw3gUumOd4soCJQ8/LXMbW2X9MBlJgLX3Zoc9wwB6g+9nqD+VakR8XsNCcgdOWxjTq/NiXXz0FGSbg6k0SMKK1s2yzK5DxQI1QGscy9oBPzTC9OXdX8YBxE/323phQRVv/C94sMgCuj+YK7+G3FcXul6RlrzVk4bI0RPY/vA/qCliLpdv4C+ZNlUDNCAk5yKRXFwv+Og/Sy8NWXpSRnUvw==
import base64
import re
import time
import uuid
import random
import json

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.plugin.api.useragents import CHROME as USER_AGENT
from ACEStream.PluginsContainer.streamlink.stream import (HTTPStream, HLSStream)

HUAJIAO_URL = "http://www.huajiao.com/l/{}"
LAPI_URL = "http://g2.live.360.cn/liveplay?stype=flv&channel={}&bid=huajiao&sn={}&sid={}&_rate=xd&ts={}&r={}" \
           "&_ostype=flash&_delay=0&_sign=null&_ver=13"

_url_re = re.compile(r"""
        http(s)?://(www\.)?huajiao.com
        /l/(?P<channel>[^/]+)
""", re.VERBOSE)

_feed_json_re = re.compile(r'^\s*var\s*feed\s*=\s*(?P<feed>{.*})\s*;', re.MULTILINE)

_feed_json_schema = validate.Schema(
    validate.all(
        validate.transform(_feed_json_re.search),
        validate.any(
            None,
            validate.all(
                validate.get('feed'),
                validate.transform(json.loads)
            )
        )
    )
)


class Huajiao(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        channel = match.group("channel")

        self.session.http.headers.update({"User-Agent": USER_AGENT})
        self.session.http.verify = False

        feed_json = self.session.http.get(HUAJIAO_URL.format(channel), schema=_feed_json_schema)
        if feed_json['feed']['m3u8']:
            stream = HLSStream(self.session, feed_json['feed']['m3u8'])
        else:
            sn = feed_json['feed']['sn']
            channel_sid = feed_json['relay']['channel']
            sid = uuid.uuid4().hex.upper()
            encoded_json = self.session.http.get(LAPI_URL.format(channel_sid, sn, sid, time.time(), random.random())).content
            decoded_json = base64.decodestring(encoded_json[0:3] + encoded_json[6:]).decode('utf-8')
            video_data = json.loads(decoded_json)
            stream = HTTPStream(self.session, video_data['main'])
        yield "live", stream


__plugin__ = Huajiao
