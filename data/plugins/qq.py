# -*- coding: utf-8 -*-
#-plugin-sig:B/+VsvXpaxrffomv7CA9vD1TRoa7UVM7Mkrc7vXYqy/ZoDaBTG4hWfI2DksA/8F1WWq3yh80J+jq1gcmC20qM/TCgW14eMw+soWaMa2t5JKBHLUsl7axWdz1QeKI/SJAEcyI81zEPYuRioJhkph5UrThHy5cjZIVGak2Y1n3tWjRzDU3oMV5ZDclM21xftEJvJlgWwz5zraf4zqKyUfDBUKRX6TVwlKmtxNsR7ataf0tkNv88BaFXk8B5I/38EBtE1iCBdORAMg/kTkd8NzKiHSWldc1H2Hs1yHfbElrZ3xSUMFPc45sROsM0QoBnlvQh9REJAqQwFcw/FGOyXIhqA==
import re

from ACEStream.PluginsContainer.streamlink.exceptions import NoStreamsError
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import parse_json
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class QQ(Plugin):
    """Streamlink Plugin for live.qq.com"""

    _data_schema = validate.Schema(
        {
            "data": {
                "hls_url": validate.text
            }
        },
        validate.get("data", {}),
        validate.get("hls_url")
    )

    api_url = "http://live.qq.com/api/h5/room?room_id={0}"

    _data_re = re.compile(r"""(?P<data>{.+})""")
    _url_re = re.compile(r"""https?://(m\.)?live\.qq\.com/(?P<room_id>\d+)""")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        match = self._url_re.match(self.url)
        if not match:
            return

        room_id = match.group("room_id")
        res = self.session.http.get(self.api_url.format(room_id))

        data = self._data_re.search(res.text)
        if not data:
            return

        try:
            hls_url = parse_json(data.group("data"), schema=self._data_schema)
        except Exception:
            raise NoStreamsError(self.url)

        self.logger.debug("URL={0}".format(hls_url))
        return {"live": HLSStream(self.session, hls_url)}


__plugin__ = QQ
