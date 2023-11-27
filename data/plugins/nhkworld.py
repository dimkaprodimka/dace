#-plugin-sig:U2Js9G/E8x/LnGEsUBbx3Il+SUWdKnirgtFZNVmGl0DfI9j/vvvD+bR+gVX0Z94KKEUFvOd5E4hh7lEreFsrJ9m62nLYG3Blp5tgix6SOGUdn5HnOEZE2ThtZ8xA44dPO4Bod0E/S+tykPtqHg9AWvxQtB2vvwcRas7/yDr+8zgcC8/yGsNUogqomhGD2Z0pepppFHw7dIczS/iJuv+D1iPIydBPqrJ6qMp80/CtwiXINeqEfT5tlJ9EurzeVpJNNpQQGNHapJ2yvQT8kzeAkD0ss8YDxLzwF6Qxoo4qnJsBGnFRSglv8ARFoD2yG9ZwcmuRoOOW0WoYhfabR80xpQ==
"""Plugin for NHK World, NHK Japan's english TV channel."""

import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

API_URL = "http://{}.nhk.or.jp/nhkworld/app/tv/hlslive_web.json"

_url_re = re.compile(r"http(?:s)?://(?:(\w+)\.)?nhk.or.jp/nhkworld")


class NHKWorld(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url) is not None

    def _get_streams(self):
        # get the HLS json from the same sub domain as the main url, defaulting to www
        sdomain = _url_re.match(self.url).group(1) or "www"
        res = self.session.http.get(API_URL.format(sdomain))

        stream_url = self.session.http.json(res)['main']['wstrm']
        return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = NHKWorld
