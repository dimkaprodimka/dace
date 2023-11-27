#-plugin-sig:luciAFo+w7hmsM1DaOBeSHW0hMzRsUZpKJX4AWXNr3M+eqw8sOdiQML4MGWoXs69aMvzAomalshym0kZRUj1/kWyjzhHv+ked2/G046h06WZHHbYy6e5oz4BGTEL0KtKImwsqKTHOLMFIvVu9Vj5wxkmbbXmparvcXO93+/fWeaYXkYccWwoWADHQiPEhubBXaQMvT0IVdIuieNeWhHc85hFEr1XDgsKxTZT0RXA37W3AzASLqkwfqbrxzuhXFN3BUDGiNyZoNrHDhgnhl3hwz4ypY0oBZ+csMa7ioBTveaa02QrpCOD/mojBFJC456DzDSDwzk0as6oSE6YehWAVg==
from __future__ import print_function
import re

from ACEStream.PluginsContainer.streamlink import streams
from ACEStream.PluginsContainer.streamlink.plugin import Plugin


class StarTV(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?startv.com.tr/canli-yayin")
    iframe_re = re.compile(r'frame .*?src="(https://www.youtube.com/[^"]+)"')

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        m = self.iframe_re.search(res.text)

        yt_url = m and m.group(1)
        if yt_url:
            self.logger.debug("Deferring to YouTube plugin with URL: {0}".format(yt_url))
            return streams(yt_url)


__plugin__ = StarTV
