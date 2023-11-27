#-plugin-sig:C5owLAhZi+sI8o5FyYW2jfLImZbZcsAlqtaF7pfWix06P3CZCVwlsKwTASjKjep1xMMHwEOU9i+/9os0u5RYv0NEpGRMbs0zyCRzJ0Mz/0CSRER/xkXCg3XQcvUW0IdSJFajdyecEx9KpGY53OB8r3yh0qBPNLmihK6w5wCxVW6TiYv1PA4VlfLMvuUL2lz2kCkgkdydv3ZhTwnqyyR7dZcJ20gKCqEMraPLVwroao2lYZPPP+FCaiYpbadT3ISDFo2qwl8Z+nAuPmsuV3PTD1YcLXI8hRfQ5Cchbke/HhcyNHmVjJYN+ICmvfyxIOwnt0KL5dA8+kJKghEPaPzkpg==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class LRT(Plugin):
    _url_re = re.compile(r"https?://(?:www\.)?lrt.lt/mediateka/tiesiogiai/.")
    _video_id_re = re.compile(r"""var\svideo_id\s*=\s*["'](?P<video_id>\w+)["']""")
    API_URL = "https://www.lrt.lt/servisai/stream_url/live/get_live_url.php?channel={0}"

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        page = self.session.http.get(self.url)
        m = self._video_id_re.search(page.text)
        if m:
            video_id = m.group("video_id")
            data = self.session.http.get(self.API_URL.format(video_id)).json()
            hls_url = data["response"]["data"]["content"]

            for s in HLSStream.parse_variant_playlist(self.session, hls_url).items():
                yield s
        else:
            log.debug("No match for video_id regex")


__plugin__ = LRT
