#-plugin-sig:ChKsOdNs8idtiFf/Un8GGUAMZ9suCXhdq0hNOqsoHjwllJt4OLqXfqMv39fLlw5XEi1VshoYV1TBK6NtjMrbeer2vB8u+feq2G8bt7tRM44ZCJ4cz11j5GQMJlwcIHpYI6YOXe9bYyoRBmX/OCe+sUapOF49zziMFASs+lBcAcXLmvcbMt7k40AGIFb3v1dO8t7gi5G+G175TnRPSo6EdgpVylxQ+qghAde+X0fWrptE1pHzZdu8nphV1CCpUMr9Bj0/mEDWtOZ4xCakqjO2wpXsi/M9U/KjLdCXgGhJq6SdFMPqCj8j3p+VT8RVEcUOHGu5q4KXKTXlpefRoAx0Mg==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json

log = logging.getLogger(__name__)


class Mitele(Plugin):
    _url_re = re.compile(r"https?://(?:www\.)?mitele\.es/directo/(?P<channel>[\w-]+)")

    pdata_url = "https://indalo.mediaset.es/mmc-player/api/mmc/v1/{channel}/live/html5.json"
    gate_url = "https://gatekeeper.mediaset.es"

    error_schema = validate.Schema({
        "code": validate.any(validate.text, int),
        "message": validate.text,
    })
    pdata_schema = validate.Schema(validate.transform(parse_json), validate.any(
        validate.all(
            {
                "locations": [{
                    "gcp": validate.text,
                    "ogn": validate.any(None, validate.text),
                }],
            },
            validate.get("locations"),
            validate.get(0),
        ),
        error_schema,
    ))
    gate_schema = validate.Schema(
        validate.transform(parse_json),
        validate.any(
            {
                "mimeType": validate.text,
                "stream": validate.url(),
            },
            error_schema,
        )
    )

    def __init__(self, url):
        super(Mitele, self).__init__(url)
        self.session.http.headers.update({
            "User-Agent": useragents.FIREFOX,
            "Referer": self.url
        })

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        channel = self._url_re.match(self.url).group("channel")

        pdata = self.session.http.get(self.pdata_url.format(channel=channel),
                                      acceptable_status=(200, 403, 404),
                                      schema=self.pdata_schema)
        log.trace("{0!r}".format(pdata))
        if pdata.get("code"):
            log.error("{0} - {1}".format(pdata["code"], pdata["message"]))
            return

        gdata = self.session.http.post(self.gate_url,
                                       acceptable_status=(200, 403, 404),
                                       data=pdata,
                                       schema=self.gate_schema)
        log.trace("{0!r}".format(gdata))
        if gdata.get("code"):
            log.error("{0} - {1}".format(gdata["code"], gdata["message"]))
            return

        log.debug("Stream: {0} ({1})".format(gdata["stream"], gdata.get("mimeType", "n/a")))
        for s in HLSStream.parse_variant_playlist(self.session,
                                                  gdata["stream"],
                                                  name_fmt="{pixels}_{bitrate}").items():
            yield s


__plugin__ = Mitele
