#-plugin-sig:Q8mS6sA97pmTPhmHl1GPO9sODf0aCgYgtL04aBg+vekLarAQrtSFEUS/IERxx8wNVM6Ai+PukKcVUiocn/bMz4ftSlLABoO1dIqMmDCIGusZLrb/mpf56FxNMebmHoMYI93UCnYGlw2qrqs8iB0IvHhR5T34if4tSXtG/WVcMZd4v+vDdRO02drz1fPTsQHziN+kqrml70u6uxLJiDk8EflOLFCQNAtE/FxBi256bLzq9WCM4h97KWKncyBgn2T9pRgG/C/298cQy91U5qVdZvl+d0lindRAVZJY9K+9I2Ls86GAM2JrahzQZSusSNLwYFPlNaKRk2yW481SGQMmLg==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api.support_plugin import theplatform
from ACEStream.PluginsContainer.streamlink.utils import update_scheme

ThePlatform = theplatform.ThePlatform

class NBCSports(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?nbcsports\.com")
    embed_url_re = re.compile(r'''id\s*=\s*"vod-player".*?\ssrc\s*=\s*"(?P<url>.*?)"''')

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        m = self.embed_url_re.search(res.text)
        platform_url = m and m.group("url")

        if platform_url:
            url = update_scheme(self.url, platform_url)
            # hand off to ThePlatform plugin
            p = ThePlatform(url)
            p.bind(self.session, "plugin.nbcsports")
            return p.streams()


__plugin__ = NBCSports
