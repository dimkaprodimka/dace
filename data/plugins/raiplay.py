#-plugin-sig:gDwg35kgraqGEiBWLmsn0R9KoB4+G8hnVCBz7ua8Eh9Nt5m1O8LTrMWWb43++NWL/dgEyDBUeawvdh33iFJrBV3tLF2iairS8BMXYnThDejn+U5QG+yvZngTWlRalA4m6ecq3USHPp5kc730myQjWymXI+hOZqZSkFQFvnkn0qceijFCnvplci9EClz9PFWyfYP3LzHAKpcoQqrmvhhFIBW9iWe2DOn/CYol2iD1CjZbbin1RfkVPlBjxqVWt0JyVOq9oXTtPN0qMun1ZYlaGYovNuBAjdD+WkYBX/8T+2T7i1dMbOaymVy0krGNVyXkjbhf0rgqRl7zUQBuaKm0Sg==
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import urlparse, urlunparse
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json


log = logging.getLogger(__name__)


class RaiPlay(Plugin):
    _re_url = re.compile(r"https?://(?:www\.)?raiplay\.it/dirette/(\w+)/?")

    _re_data = re.compile(r"data-video-json\s*=\s*\"([^\"]+)\"")
    _schema_data = validate.Schema(
        validate.transform(_re_data.search),
        validate.any(None, validate.get(1))
    )
    _schema_json = validate.Schema(
        validate.transform(parse_json),
        validate.get("video"),
        validate.get("content_url"),
        validate.url()
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._re_url.match(url) is not None

    def _get_streams(self):
        json_url = self.session.http.get(self.url, schema=self._schema_data)
        if not json_url:
            return

        json_url = urlunparse(urlparse(self.url)._replace(path=json_url))
        log.debug("Found JSON URL: {0}".format(json_url))

        stream_url = self.session.http.get(json_url, schema=self._schema_json)
        log.debug("Found stream URL: {0}".format(stream_url))

        res = self.session.http.request("HEAD", stream_url)
        # status code will be 200 even if geo-blocked, so check the returned content-type
        if not res or not res.headers or res.headers["Content-Type"] == "video/mp4":
            log.error("Geo-restricted content")
            return

        for stream in HLSStream.parse_variant_playlist(self.session, stream_url).items():
            yield stream


__plugin__ = RaiPlay
