#-plugin-sig:nL7r4GnIGyVosDLwidl/CekP+akfGKQAPYbML1obCNr06EKexXQWNaG9577n/WF73oUl56sjcFY69d7fdKPA5w4qrqG+/ZizEukYBVGNuE4wD/q0A+cPGchdUzKsYI82aN+VKkYrO5biQU14qaBg2YMnIMay7cVULMbmw5ILLejSrU6MwyNzyPhG8AVEo09vhjHMPDkF55kqOFlziTPHveJCXFhcbRoHBoaoC24zXUAow6265lnMaHU7WXQI3broaDBZziL50w3CikxpWP7lLE62/EYz4x40MjdqBrF2Q1K2+yeY45J6V966aDq3NReGqXPhOtFG76QoDXA2tajqew==
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import urlparse, parse_qsl
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import itertags
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class Mjunoon(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?mjunoon\.tv/")

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        self.session.http.headers.update({"User-Agent": useragents.FIREFOX})
        res = self.session.http.get(self.url)
        for script in itertags(res.text, 'script'):
            if script.attributes.get("id") == "playerScript":
                log.debug("Found the playerScript script tag")
                urlparts = urlparse(script.attributes.get("src"))
                i = 0

                for key, url in parse_qsl(urlparts.query):
                    if key == "streamUrl":
                        i += 1
                        for s in HLSStream.parse_variant_playlist(self.session, url, params=dict(id=i), verify=False).items():
                            yield s


__plugin__ = Mjunoon
