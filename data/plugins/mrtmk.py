#-plugin-sig:EtyZKDLQN+MuSjDSh6zVNiXNLp9+pKEwoTlW/V1ZzPSH4TpD8HsyPB0+rVwfpqhcsDVcNPpaof3q2BVOWS+LzyUHwGnzzNQTffU9Ttv2Eh27/MVy2OrcAH/DKTrgM+OjJg8FwACCv9VPYhzs8pjrXgEBJBWs8XO2/sGLt8odiQgJVdd6gmnLotqw+tnd10W7RibwrRJzuru32zTNG51OZRY2GLxDIkQRkJJrYfZ9S4iZiBmTTNNk7OfAnh5jVvm7CXJsg4YFECrvxYJWuraQmCzRcbaLK2nRsGGQpake8M0ItDQaSCgIZqKChWu4tpw/8FuO4KT3T7jKC6JyCAt4hA==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class MRTmk(Plugin):
    url_re = re.compile(r"""https?://play.mrt.com.mk/(live|play)/""")
    file_re = re.compile(r"""(?P<url>https?://vod-[\d\w]+\.interspace\.com[^"',]+\.m3u8[^"',]*)""")

    stream_schema = validate.Schema(
        validate.all(
            validate.transform(file_re.finditer),
            validate.transform(list),
            [validate.get("url")],
            # remove duplicates
            validate.transform(set),
            validate.transform(list),
        ),
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        stream_urls = self.stream_schema.validate(res.text)
        log.debug("Found streams: {0}".format(len(stream_urls)))
        if not stream_urls:
            return

        for stream_url in stream_urls:
            try:
                for s in HLSStream.parse_variant_playlist(self.session, stream_url).items():
                    yield s
            except IOError as err:
                if "403 Client Error" in str(err):
                    log.error("Failed to access stream, may be due to geo-restriction")
                else:
                    raise err


__plugin__ = MRTmk
