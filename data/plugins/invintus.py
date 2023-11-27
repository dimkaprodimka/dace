#-plugin-sig:gAobb37+b+iK3dHHA2DeSdE/GgrKclhu1BxWIdgznSIifqUrMcOn/XVAfj6Op94z/C021qFBJMluJKRIN36jC4i7ZlyJcvop0ovNyWQC5AMN62IWBunnwKM0nEGiFBhW7oJq/YPyXDxEullS9G8uEEkIHRhf+QgjJzINo6YJA51h/QKJEdbgqe9wgNxZVHda+PVspaNxlRZyxGF7hVER0Li5LUxNvcCUNTSqy8DiQZPBdoFopJnFJmj38sAatGVjY6gakvsNqxyrroK/WO4NhMt/GEYn2EE4bmzChPExf2MUuklA40bQPoClUvimvJrClvKIJUy/C9qc+A49ZbGhwA==
import re
import json

from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils.url import update_scheme


class InvintusMedia(Plugin):
    WSC_API_KEY = "7WhiEBzijpritypp8bqcU7pfU9uicDR"  # hard coded in the middle of https://player.invintus.com/app.js
    API_URL = "https://api.v3.invintusmedia.com/v2/Event/getDetailed"

    url_re = re.compile(r"https?://player\.invintus\.com/\?clientID=(\d+)&eventID=(\d+)")
    api_response_schema = validate.Schema({"data": {"streamingURIs": {"main": validate.url()}}})

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        m = self.url_re.match(self.url)
        postdata = {
            "clientID": m.group(1),
            "showEncoder": True,
            "showMediaAssets": True,
            "showStreams": True,
            "includePrivate": False,
            "advancedDetails": True,
            "VAST": True,
            "eventID": m.group(2)
        }
        headers = {
            "Content-Type": "application/json",
            "wsc-api-key": self.WSC_API_KEY,
            "Authorization": "embedder"
        }
        res = self.session.http.post(self.API_URL, data=json.dumps(postdata), headers=headers)
        api_response = self.session.http.json(res, schema=self.api_response_schema)
        if api_response is None:
            return

        hls_url = api_response["data"]["streamingURIs"]["main"]
        return HLSStream.parse_variant_playlist(self.session, update_scheme(self.url, hls_url))


__plugin__ = InvintusMedia
