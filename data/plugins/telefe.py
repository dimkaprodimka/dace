#-plugin-sig:FqMEvuNwrhxDGgRlxXmTeIIX06gtMPf2STg7mNS8d4ce5SNaGsWR0AVDBlpM+w8r/795KtSiXo/7csuBtYIzxZbYNU7JFNfX3gf48hHtddLJICgi6HxbFy+DSs9BVSKV+rG8CKO5fnsLnfVo3RVdUh4GFkYq+ZtI1d/ieEEwDx/s+LZl+oqw0ZdAt3TPdfZIbLY5AH/Ocm9/nyxfz92uNOV/UM6jBFNYyo09hGp136umos5qS9oifGcbSRR02LRxQiB6NFORO8o0Dt4kqDRQ0BctPBGfrNfHbd+sSOUGdm43Pa5MiXC1P5pH3qivGUjMqYs3g9htq2pBm41+Yj+LUQ==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.stream import HLSStream, HTTPStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json


class Telefe(Plugin):
    _url_re = re.compile(r'https?://telefe.com/.+')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        res = self.session.http.get(self.url, headers={'User-Agent': useragents.CHROME})
        video_search = res.text
        video_search = video_search[video_search.index('{"top":{"view":"PlayerContainer","model":{'):]
        video_search = video_search[: video_search.index('}]}}') + 4] + "}"

        video_url_found_hls = ""
        video_url_found_http = ""

        json_video_search = parse_json(video_search)
        json_video_search_sources = json_video_search["top"]["model"]["videos"][0]["sources"]
        self.logger.debug('Video ID found: {0}', json_video_search["top"]["model"]["id"])
        for current_video_source in json_video_search_sources:
            if "HLS" in current_video_source["type"]:
                video_url_found_hls = "http://telefe.com" + current_video_source["url"]
                self.logger.debug("HLS content available")
            if "HTTP" in current_video_source["type"]:
                video_url_found_http = "http://telefe.com" + current_video_source["url"]
                self.logger.debug("HTTP content available")

        self.session.http.headers = {
            'Referer': self.url,
            'User-Agent': useragents.CHROME,
            'X-Requested-With': 'ShockwaveFlash/25.0.0.148'
        }

        if video_url_found_hls:
            hls_streams = HLSStream.parse_variant_playlist(self.session, video_url_found_hls)
            for s in hls_streams.items():
                yield s

        if video_url_found_http:
            yield "http", HTTPStream(self.session, video_url_found_http)


__plugin__ = Telefe
