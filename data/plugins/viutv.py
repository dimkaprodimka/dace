#-plugin-sig:KhCy9KHNhmtRGCafiFFTUACs4eqP7Yycx4cG4hmqrsikd+ImIfEWvBkUvmPtASI7WcyYAbyMSBEnKSF5bvfv6Hle/gJzGO0bjGorCTFUKZJjw9/L/RNn8YTZN1vpfEgZK1EPEhDQuKwsp6Wzt2U5GhpfIMkjKjfaTGBIvG4BTJ5bpwJL1pmpr8bdtymzbDw7/yqoVUmtqhdHli6bMBYE9iwsiFy+hUkiSFs+g4kWSb79RkjLdvB5MBbOjfIvwo2EbEQ9WIP3T3M5rsDcwlhaoKPWBiH/cU6GV37oRegPm/7aKkPpb1nU4RasRn4NQahkcYs0rYE+Vns3BFZXIiD3Wg==
import datetime
import logging
import random
import re
import json

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class ViuTV(Plugin):
    _url_re = re.compile(r"https?://viu\.tv/ch/(\d+)")
    api_url = "https://api.viu.now.com/p8/2/getLiveURL"

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    @property
    def device_id(self):
        return "".join(random.choice("abcdef0123456789") for _ in range(18))

    @property
    def channel_id(self):
        return self._url_re.match(self.url).group(1)

    def _get_streams(self):
        api_res = self.session.http.post(self.api_url,
                                         headers={"Content-Type": 'application/json'},
                                         data=json.dumps({"callerReferenceNo": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                                                          "channelno": self.channel_id.zfill(3),
                                                          "mode": "prod",
                                                          "deviceId": self.device_id,
                                                          "deviceType": "5",
                                                          "format": "HLS"}))
        data = self.session.http.json(api_res)
        if data['responseCode'] == 'SUCCESS':
            for stream_url in data.get("asset", {}).get("hls", {}).get("adaptive", []):
                return HLSStream.parse_variant_playlist(self.session, stream_url)
        else:
            log.error("Failed to get stream URL: {0}".format(data['responseCode']))


__plugin__ = ViuTV
