#-plugin-sig:m3c3jiTnIIHKbsJFhoZFT0stG6E9zonZ0jSiKnxdHib3KfFxK3aExCjh101lNdCBxumC01dWWxJr+uKxypSe9kOeQaG2Jn+iqJr/ctbfgKYiaGSo5hBIPdLxrxQP318kNc3UMi0/QMvQhrGgGa25yYzH//tR/X6kWNxC5cSJt5ZSzs+1wH4LWDDB41bNtV9w3OouWn3RDpaqX/Oq4I0d8wzRRK6W98+5MvphBd/y5kbf5oAByw1yn3FG0QU/wKTAkUFfONiOila+wrqDI38V15A4PZsWa15AFq04aVrmzfBAXK9LGs4q46LEtmH2lM8lh0SNRknxqbjOnjnzJ4cl7A==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json, update_scheme

log = logging.getLogger(__name__)


class Sportschau(Plugin):
    _re_url = re.compile(r"https?://(?:\w+\.)*sportschau.de/")

    _re_player = re.compile(r"https?:(//deviceids-medp.wdr.de/ondemand/\S+\.js)")
    _re_json = re.compile(r"\$mediaObject.jsonpHelper.storeAndPlay\(({.+})\);?")

    _schema_player = validate.Schema(
        validate.transform(_re_player.search),
        validate.any(None, validate.Schema(
            validate.get(1),
            validate.transform(lambda url: update_scheme("https:", url))
        ))
    )
    _schema_json = validate.Schema(
        validate.transform(_re_json.match),
        validate.get(1),
        validate.transform(parse_json),
        validate.get("mediaResource"),
        validate.get("dflt"),
        validate.get("videoURL"),
        validate.transform(lambda url: update_scheme("https:", url))
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._re_url.match(url) is not None

    def _get_streams(self):
        player_js = self.session.http.get(self.url, schema=self._schema_player)
        if not player_js:
            return

        log.debug("Found player js {0}".format(player_js))

        hls_url = self.session.http.get(player_js, schema=self._schema_json)

        for stream in HLSStream.parse_variant_playlist(self.session, hls_url).items():
            yield stream


__plugin__ = Sportschau
