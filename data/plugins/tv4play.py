#-plugin-sig:jdkc51gsL1u/5j55tqXwalRd83+gTRRJ9eI7bQ/Pwefvqaj6mpJ+M1xvxBf1ujeVUtQSh7dbEGcD9Cr7dbhEAdHJm8vQh+33fxJOFbRKDHTX4E15ij8PgofN4BuGPuFZWtCqQ8mHuRnumKRu67cytLuCkZUYObPf/k1o0IuECjZuttanHaP/4+gh1kXHBRoTYp1uO79JWglsXRaok5IoTxVxTYJ6IYMIEFGN7MyIvfs9rsaqGMdQfGjO3L0qTI3ZIKOKU3uWTeUg2a0Owx1WvuvPUmSPb5IGaFjOh4mWmVNW2pwaCEk7wMKHUvtn6pycSZhgXlSbGZIRvWW3RVLUKA==
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import urljoin
from ACEStream.PluginsContainer.streamlink.exceptions import PluginError
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class TV4Play(Plugin):
    """Plugin for TV4 Play, swedish TV channel TV4's streaming service."""

    title = None
    video_id = None

    api_url = "https://playback-api.b17g.net"
    api_assets = urljoin(api_url, "/asset/{0}")

    _url_re = re.compile(r"""
        https?://(?:www\.)?
        (?:
            tv4play.se/program/[^\?/]+
            |
            fotbollskanalen.se/video
        )
        /(?P<video_id>\d+)
    """, re.VERBOSE)

    _meta_schema = validate.Schema(
        {
            "metadata": {
                "title": validate.text
            },
            "mediaUri": validate.text
        }
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    @property
    def get_video_id(self):
        if self.video_id is None:
            match = self._url_re.match(self.url)
            self.video_id = match.group("video_id")
            log.debug("Found video ID: {0}".format(self.video_id))
        return self.video_id

    def get_metadata(self):
        params = {
            "device": "browser",
            "protocol": "hls",
            "service": "tv4",
        }
        try:
            res = self.session.http.get(
                self.api_assets.format(self.get_video_id),
                params=params
            )
        except Exception as e:
            if "404 Client Error" in str(e):
                raise PluginError("This Video is not available")
            raise e
        log.debug("Found metadata")
        metadata = self.session.http.json(res, schema=self._meta_schema)
        self.title = metadata["metadata"]["title"]
        return metadata

    def get_title(self):
        if self.title is None:
            self.get_metadata()
        return self.title

    def _get_streams(self):
        metadata = self.get_metadata()

        try:
            res = self.session.http.get(urljoin(self.api_url, metadata["mediaUri"]))
        except Exception as e:
            if "401 Client Error" in str(e):
                raise PluginError("This Video is not available in your country")
            raise e

        log.debug("Found stream data")
        data = self.session.http.json(res)
        hls_url = data["playbackItem"]["manifestUrl"]
        log.debug("URL={0}".format(hls_url))
        for s in HLSStream.parse_variant_playlist(self.session,
                                                  hls_url).items():
            yield s


__plugin__ = TV4Play
