#-plugin-sig:UABDpFSX7+eWHkztTHh8I3BNCw61VaTXK4K6I28mzR3ToclXxwz/3JENz7mtIVGaj12ysbDAk4vU+8sBLG8x1Ofmy5WCZFsbOHbSS//K5hbSX1FzVzOV4U34pia6rbPKT60IY+l9oPJL1tft3JM0d9T+1Q8zd7xm2Zwf+JivY2klW6JAe4sfE27IhLMVwE32nPqIlrVjVlIlki8rw/B50wjQZFehpYfN2tfVowdzO/RAFJGYcv9b8JE6umZJBenehvqgfUweuJnGFE3R95bwShRqCgsL1mPll3T6a6x8L23CEsl7Hev6sRWzOOH0BFd2jmilvLjqDJ/uZrmTAhB68Q==
import re

from ACEStream.PluginsContainer.streamlink.exceptions import NoStreamsError
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

STREAM_INFO_URL = "https://api.periscope.tv/api/v2/getAccessPublic"

STATUS_GONE = 410
STATUS_UNAVAILABLE = (STATUS_GONE,)

_url_re = re.compile(r"http(s)?://(www\.)?(periscope|pscp)\.tv/[^/]+/(?P<broadcast_id>[\w\-\=]+)")
_stream_schema = validate.Schema(
    validate.any(
        None,
        validate.union({
            "hls_url": validate.all(
                {"hls_url": validate.url(scheme="http")},
                validate.get("hls_url")
            ),
        }),
        validate.union({
            "replay_url": validate.all(
                {"replay_url": validate.url(scheme="http")},
                validate.get("replay_url")
            ),
        }),
    ),
)


class Periscope(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        res = self.session.http.get(
            STREAM_INFO_URL,
            params=match.groupdict(),
            acceptable_status=STATUS_UNAVAILABLE
        )

        if res.status_code in STATUS_UNAVAILABLE:
            return

        data = self.session.http.json(res, schema=_stream_schema)
        if data.get("hls_url"):
            hls_url = data["hls_url"]
            hls_name = "live"
        elif data.get("replay_url"):
            self.logger.info("Live Stream ended, using replay instead")
            hls_url = data["replay_url"]
            hls_name = "replay"
        else:
            raise NoStreamsError(self.url)

        streams = HLSStream.parse_variant_playlist(self.session, hls_url)
        if not streams:
            return {hls_name: HLSStream(self.session, hls_url)}
        else:
            return streams


__plugin__ = Periscope
