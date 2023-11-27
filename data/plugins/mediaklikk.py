#-plugin-sig:MI911dr5805WSBahR3cQhu3UXklFmCT+Wt7fzSEBc/l0Q+fhYKNSVSwhA7s6NUghUU3BEvpdN0QFuaX1+7LC62T7sJ2a0AjZmV7nfUpYlliZJr8Xofz+LMEk2XT4WUfqoVJAc//kMXzZ8I/Co9LzRaWPg2mN+LCLrvWzc7EFoH4lRVvksIu4IWD3EjcvcxDIYs8cQHXuubuQdwxo5gklMQS58rP8J/vn5y5MLU7nj9qolAk8LzgSPndlaxvXuysu+A9mM4i7tXVwer8/R9HqvE1phmd0/FnB85+1wfmTX5QobDaXNkaB54SrUYMF7kOUzG+USF8XJ3lWJ+VDR9MnZg==
import logging
import re

from ACEStream.PluginsContainer.streamlink.exceptions import PluginError
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils.url import update_scheme

log = logging.getLogger(__name__)


class Mediaklikk(Plugin):
    PLAYER_URL = "https://player.mediaklikk.hu/playernew/player.php"

    _url_re = re.compile(r"https?://(?:www\.)?mediaklikk\.hu/[\w\-]+\-elo/?")
    _id_re = re.compile(r'"streamId":"(\w+)"')
    _file_re = re.compile(r'"file":\s*"([\w\./\\=:\-\?]+)"')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        # get the stream id
        res = self.session.http.get(self.url)
        m = self._id_re.search(res.text)
        if not m:
            raise PluginError("Stream ID could not be extracted.")

        # get the m3u8 file url
        params = {
            "video": m.group(1),
            "noflash": "yes",
        }
        res = self.session.http.get(self.PLAYER_URL, params=params)
        m = self._file_re.search(res.text)
        if m:
            url = update_scheme("https://",
                                m.group(1).replace("\\/", "/"))

            log.debug("URL={0}".format(url))
            return HLSStream.parse_variant_playlist(self.session, url)


__plugin__ = Mediaklikk
