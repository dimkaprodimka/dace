#-plugin-sig:Fd7ZdqKEIjIJimaEbcyl1uhhUUtAOFWFZ1w1u2B5SqjL8Xi4uAdR4AUw4j0vpQTFK3LcwJ+zvB4IV8aLTFmcNKzLLkHJHlsOIR4bl/5lwyhyMC9RqevC+Dy0G2BJMfwUYHmt6WL4JPtvIFA1s4q/Who4RZ7D69eduAWBCrzXLy5b2rmAY0C3oTaDl8RIr1pjLWXCmTCuLQRb1/yo+HGYUZmkb0XA2ovLxkCFt3qGsIoxPIABVr0CHGTZwNAtwVNO2G4rPI200OGy+Iqbqo3pG69VjmRz82MdRT7/F18FERczmLC8TdK9KNdfwT9kX9YWAGG7AgZUR7TVI14v2fxFxQ==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class Tvibo(Plugin):

    _url_re = re.compile(r"https?://player\.tvibo\.com/\w+/(?P<id>\d+)")
    _api_url = "http://panel.tvibo.com/api/player/streamurl/{id}"

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        channel_id = self._url_re.match(self.url).group("id")

        api_response = self.session.http.get(
            self._api_url.format(id=channel_id),
            acceptable_status=(200, 404))

        data = self.session.http.json(api_response)
        log.trace("{0!r}".format(data))
        if data.get("st"):
            yield "source", HLSStream(self.session, data["st"])
        elif data.get("error"):
            log.error(data["error"]["message"])


__plugin__ = Tvibo
