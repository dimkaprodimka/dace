#-plugin-sig:hggvn1dbmuYukZm8u/vfcHKMgzeL5zMohak0bNJ8QNj7vSiQL4gP2k9WjsY2KqaT441EgofRYfiv8U9wmkNwfp9IdBaVmRo33uXF24Zt3lDVFZE4IcSpDfF94QTgE35ZSUFEzumjVAwyebowolJlobGtHaYwiQ2IQ+6UHRfRBCnTChHVD+S8+r9RnLKuOd58vduI/SJyo5JsM0Uvq1SWSLyCG8vYZHadWhDQyikrLVD7C0Y6YXExdMMTxphnCDnZhnlPZ8kZ8QXOvXXB/NYN/T2ES/PAsVnZxGghIFYS7bcGFSLxod/wBRx8SN0mZusAlRv71FL97PVAILTRS06mdg==
import re
import logging

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json

log = logging.getLogger(__name__)


class Stadium(Plugin):
    url_re = re.compile(r"""https?://(?:www\.)?watchstadium\.com/live""")
    API_URL = "https://player-api.new.livestream.com/accounts/{account_id}/events/{event_id}/stream_info"
    _stream_data_re = re.compile(r"var StadiumSiteData = (\{.*?});", re.M | re.DOTALL)

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        m = self._stream_data_re.search(res.text)
        if m:
            data = parse_json(m.group(1))
            if data['LivestreamEnabled'] == '1':
                account_id = data['LivestreamArgs']['account_id']
                event_id = data['LivestreamArgs']['event_id']
                log.debug("Found account_id={0} and event_id={1}".format(account_id, event_id))

                url = self.API_URL.format(account_id=account_id, event_id=event_id)
                api_res = self.session.http.get(url)
                api_data = self.session.http.json(api_res)
                stream_url = api_data.get('secure_m3u8_url') or api_data.get('m3u8_url')
                if stream_url:
                    return HLSStream.parse_variant_playlist(self.session, stream_url)
                else:
                    log.error("Could not find m3u8_url")
            else:
                log.error("Stream is offline")


__plugin__ = Stadium
