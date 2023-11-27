#-plugin-sig:ZhZAV3ib2Ew2p3vINHAWKfCjvirF6Rtxt3HVxsUhBRV5cqCY9sjrK5Dlet7uBljQLUtR4kOUpH446uH1ow/bc1UWhyXxZA3cf0o8yNtBgf5q8+xbtiUtFmHAbeU2cIcNLT+c7kxrB3dhoE2Lyzs+DBCRZqZWpA8fJ/gWRIpFxaof69mOd9N0BxPnAcUdN7XIFFfJt9Ubq8SsXn1Fx0mwa6Y2dzpmLd02lXZDA4c6+9YJ5shomjuGFqfUrZo0IGxipOTka5LcKg2Od086LCugh/CzYS1NDDdfPBmAx/EIxbNEiQMEWgfcBiRH7sFuAvxQgP0GQSbTU8Eazncw0VMljQ==
from __future__ import print_function

import json
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream, HTTPStream
from ACEStream.PluginsContainer.streamlink.utils import update_scheme


class INE(Plugin):
    url_re = re.compile(r"""https://streaming.ine.com/play\#?/
            ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?
            (.*?)""", re.VERBOSE)
    play_url = "https://streaming.ine.com/play/{vid}/watch"
    js_re = re.compile(r'''script type="text/javascript" src="(https://content.jwplatform.com/players/.*?)"''')
    jwplayer_re = re.compile(r'''jwConfig\s*=\s*(\{.*\});''', re.DOTALL)
    setup_schema = validate.Schema(
        validate.transform(jwplayer_re.search),
        validate.any(
            None,
            validate.all(
                validate.get(1),
                validate.transform(json.loads),
                {"playlist": validate.text},
                validate.get("playlist")
            )
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        vid = self.url_re.match(self.url).group(1)
        self.logger.debug("Found video ID: {0}", vid)

        page = self.session.http.get(self.play_url.format(vid=vid))
        js_url_m = self.js_re.search(page.text)
        if js_url_m:
            js_url = js_url_m.group(1)
            self.logger.debug("Loading player JS: {0}", js_url)

            res = self.session.http.get(js_url)
            metadata_url = update_scheme(self.url, self.setup_schema.validate(res.text))
            data = self.session.http.json(self.session.http.get(metadata_url))

            for source in data["playlist"][0]["sources"]:
                if source["type"] == "application/vnd.apple.mpegurl":
                    for s in HLSStream.parse_variant_playlist(self.session, source["file"]).items():
                        yield s
                elif source["type"] == "video/mp4":
                    yield "{0}p".format(source["height"]), HTTPStream(self.session, source["file"])


__plugin__ = INE
