#-plugin-sig:ZQyvwa0bNWKtx/6hQBxb3/IJxCUN1QeOoKrwmEPlnTAesu/j2GNnYNn0XjrA8+NFoDoj+Mod5wln18vpgStJGbFmRrunvPDShiW5v3QIVkz8/zMZac5gZ3ZVj2uyWqtAOhfgd6nSw0LU8SN2e9KF3ozBgqm58J08Ds5Q0FETEnbs35fJPhlzJ5YD8AA+CaY8fjwYXgE7A3o/R12a+mx/L5uLEKvScLNjoN3qfQGdEJeuKoCspN5pkGAGw9AaGKPePTUAVJ0ija/dPYQnAlvIM9PXPLVB9vAQ9MaRp3if+BEXNfIseGXveHXnULb9+VWri/LB2URjLyPOt7kZf+Hnmw==
import argparse
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin, PluginArguments, PluginArgument
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json

log = logging.getLogger(__name__)


class BTV(Plugin):
    arguments = PluginArguments(
        PluginArgument(
            "username",
            help=argparse.SUPPRESS
        ),
        PluginArgument(
            "password",
            sensitive=True,
            help=argparse.SUPPRESS
        )
    )

    url_re = re.compile(r"https?://(?:www\.)?btvplus\.bg/live/?")
    api_url = "https://btvplus.bg/lbin/v3/btvplus/player_config.php"

    media_id_re = re.compile(r"media_id=(\d+)")
    src_re = re.compile(r"src: \"(http.*?)\"")
    api_schema = validate.Schema(
        validate.all(
            {"status": "ok", "config": validate.text},
            validate.get("config"),
            validate.all(
                validate.transform(src_re.search),
                validate.any(
                    None,
                    validate.get(1),
                    validate.url()
                )
            )
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def get_hls_url(self, media_id):
        res = self.session.http.get(self.api_url, params=dict(media_id=media_id))
        return parse_json(res.text, schema=self.api_schema)

    def _get_streams(self):
        res = self.session.http.get(self.url)
        media_match = self.media_id_re.search(res.text)
        media_id = media_match and media_match.group(1)
        if media_id:
            log.debug("Found media id: {0}", media_id)
            stream_url = self.get_hls_url(media_id)
            if stream_url:
                return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = BTV
