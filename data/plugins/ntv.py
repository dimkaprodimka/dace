#-plugin-sig:Hoq4nfrGnAjm8PPrqTmOwQWVaAdyHHklWysGbmKqWbB4pBLjhzOnW1jqWUNbqWX8cbvsCGHt5lK9xUAKe9CL9T09/Yj5HH6OBPI73lwi/utcsFfJKVqkKEgytijwqsT6kYbLW2ayRyyp1Ufdyi27Wdrsi0GoGWPc3kErylkSDUDtyxzrjfxNSF/4Iw80cmZSCfnZcsHrgglUIkyzVHg7UzAoaNiDYid4C5wAZvjN3n0rtKCBpmXAMdzzhbPkfOIkCgi0oYVlD+p8ZjFGX2JSItfsFBc5VYB4kYXfafyw+JOHe8DwOOsLPpS3fQm4N3ak8iK3CA3jXHgI6OX6fciTkg==
import re
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class NTV(Plugin):
    url_re = re.compile(r'https?://www.ntv.ru/air/.*')

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        body = self.session.http.get(self.url).text
        mrl = None
        match = re.search(r'var camHlsURL = \'(.*)\'', body)
        if match:
            mrl = 'http:' + match.group(1)
        else:
            match = re.search(r'var hlsURL = \'(.*)\'', body)
            if match:
                mrl = match.group(1)
        if mrl:
            return HLSStream.parse_variant_playlist(self.session, mrl)


__plugin__ = NTV
