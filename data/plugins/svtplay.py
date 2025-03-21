#-plugin-sig:Kg8np2HPB0yeQwMacrq/pHY3fd5bm5YToxeW0xUhKk281GQvthCoCwNa9OfxyFFcq0ZHVHf0Yw47rxKjK+OkM2p127GbUPitCgFURQbG1UFH/oofkQ+l8Od9eYyRSjEztKl7AZB7s7CGtZLCSBmKHNMTKE6RHxffrkcR5xPcR30kdwmlD89h+iA43a0Sv4GaruLC4sBCrfawLsECSGsQpyiiOfzWz+UnXxKDU0ipxmbh7AwkDbJX3vcqzax2CnOPwdEE7cJAw8+RMLBub1HCktqcGHZ1tpJ/5cjuOPYtJJECmRw20+WJBBTtGGc52/bMhj5kC3JDfXY1A+pn+4bEYg==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import StreamMapper, validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream, HDSStream

API_URL = "http://www.svt.se/videoplayer-api/video/{0}"

_url_re = re.compile(r"""
    http(s)?://
    (www\.)?
    (?:
        svtplay |
        svtflow |
        oppetarkiv
    )
    .se
""", re.VERBOSE)

# Regex to match video ID
_id_re = re.compile(r"""data-video-id=['"](?P<id>[^'"]+)['"]""")
_old_id_re = re.compile(r"/(?:video|klipp)/(?P<id>[0-9]+)/")

# New video schema used with API call
_video_schema = validate.Schema(
    {
        "videoReferences": validate.all(
            [{
                "url": validate.text,
                "format": validate.text
            }],
        ),
    },
    validate.get("videoReferences")
)

# Old video schema
_old_video_schema = validate.Schema(
    {
        "video": {
            "videoReferences": validate.all(
                [{
                    "url": validate.text,
                    "playerType": validate.text
                }],
            ),
        }
    },
    validate.get("video"),
    validate.get("videoReferences")
)


class SVTPlay(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _create_streams(self, stream_type, parser, video):
        try:
            streams = parser(self.session, video["url"])
            return streams.items()
        except IOError as err:
            self.logger.error("Failed to extract {0} streams: {1}",
                              stream_type, err)

    def _get_streams(self):
        # Retrieve URL page and search for new type of video ID
        res = self.session.http.get(self.url)
        match = _id_re.search(res.text)

        # Use API if match, otherwise resort to old method
        if match:
            vid = match.group("id")
            res = self.session.http.get(API_URL.format(vid))

            videos = self.session.http.json(res, schema=_video_schema)
            mapper = StreamMapper(cmp=lambda format, video: video["format"] == format)
            mapper.map("hls", self._create_streams, "HLS", HLSStream.parse_variant_playlist)
            mapper.map("hds", self._create_streams, "HDS", HDSStream.parse_manifest)
        else:
            res = self.session.http.get(self.url, params=dict(output="json"))
            videos = self.session.http.json(res, schema=_old_video_schema)

            mapper = StreamMapper(cmp=lambda type, video: video["playerType"] == type)
            mapper.map("ios", self._create_streams, "HLS", HLSStream.parse_variant_playlist)
            mapper.map("flash", self._create_streams, "HDS", HDSStream.parse_manifest)

        return mapper(videos)


__plugin__ = SVTPlay
