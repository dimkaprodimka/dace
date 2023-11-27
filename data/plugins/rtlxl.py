#-plugin-sig:EllY2qJUlygU6L40HtHfWcxNc+e9RATzZYfFSTx/ttKBYiM7+vDfHGeGV+EFiHuzXClGeNngiBQ6qChTmTf2Kka+t8u2E+qBc2hCUpJ9w2qPVGBQixL1uXbKGCTHoXz0zBgwGIk0Ucdd75QsfXSSHsvBrPSd5cV+2E7scqneRny9J0BzjHKFH37VTYy46lYOZL3NI2L9RLa+wn7mJZC0drVJYg3852OyapDB/kqq07JEKqg7ewZYmc0Hds6i/uoGNayhm/MlFFNGWZDkAd3KsmWpy4Y4bIO8mj0Ta//9JxehdiRFYjaF9UmVkvs8Z+knoH0KJKUq5YxN6t/8GKnVxQ==
import re
import json

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

_url_re = re.compile(r"http(?:s)?://(?:\w+\.)?rtl.nl/video/(?P<uuid>.*?)\Z", re.IGNORECASE)


class rtlxl(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        uuid = match.group("uuid")
        videourlfeed = self.session.http.get(
            'https://tm-videourlfeed.rtl.nl/api/url/{}?device=pc&drm&format=hls'.format(uuid)
        ).text

        videourlfeedjson = json.loads(videourlfeed)
        playlist_url = videourlfeedjson["url"]

        return HLSStream.parse_variant_playlist(self.session, playlist_url)


__plugin__ = rtlxl
