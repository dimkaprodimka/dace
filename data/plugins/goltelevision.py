#-plugin-sig:YC6e+vtAQWMLQbUinEoCPJYkGtvCfGKmd1MjOPGCqEkTuiJgsCb+2nxGF1rLsOwKugU5xf5C1YJ0MZ5bQmyVd3DrCX1V44EaegLqAp/vNkk1k3GsPFhEeQ5BEQRHYZ5z5e61ZVPy1Q1mAgHeJ01Lkl/l61H8hc0VK8r07JDYSd2QNgqUPc6o2/NFsgNIpS0emvP82MKlii3+bY6aRpmcxPyk9yw9q6PS2+18HKI63AsnInsXN+wSVYBWzTs9gg9libaz7/tHbRgJ5u+tW2hH1k3YE0HP6kNf9Xwi7xEQr6S8/YGBl2oMzbtVFqgn2Y2zIzJHoACp+rpVS79BwvQRhg==
from __future__ import print_function, absolute_import

import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json


class GOLTelevision(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?goltelevision\.com/live")
    api_url = "https://api.goltelevision.com/api/v1/media/hls/service/live"
    api_schema = validate.Schema(validate.transform(parse_json), {
        "code": 200,
        "message": {
            "success": {
                "manifest": validate.url()
            }
        }
    }, validate.get("message"), validate.get("success"), validate.get("manifest"))

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        return HLSStream.parse_variant_playlist(self.session,
                                                self.session.http.get(self.api_url, schema=self.api_schema))


__plugin__ = GOLTelevision
