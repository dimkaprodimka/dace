#-plugin-sig:GlAMqGVok+j0qb45TSmDm3ISZ5NA6/7i3cLnNNvDZNV/IJed2SeGLW/2hZF6vdjPyX2219HHUIVhC29Dnkz/F0T8VbRMIiRYLxaUvHxn+Y5lyQ5kytcpHNPN6r2qBYSSjRG2urLZsBLddKG6K0Ykv9OUdGlSrNuKLo+vMsDiQu/x1ZRF06yy4RPatSOTh0ix1OoM75xPzEk99NSeEnAz/NNHE1LvuwKGC3YQESP4h0Qh+LpgkkcOaczDdlp45i+90ChQ5OQVAv7mEmO07fAD0v/vlonIAmQxO+R33f4rIi+8fPtgyWAx9lgwcebFp5gL/8N6olP06qzAjzZF0w6z/Q==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class ThePlatform(Plugin):
    """
    Plugin to support streaming videos hosted by thePlatform
    """
    url_re = re.compile(r"https?://player.theplatform.com/p/")
    release_re = re.compile(r'''tp:releaseUrl\s*=\s*"(.*?)"''')
    video_src_re = re.compile(r'''video.*?src="(.*?)"''')

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        m = self.release_re.search(res.text)
        release_url = m and m.group(1)
        if release_url:
            api_url = release_url + "&formats=m3u,mpeg4"
            res = self.session.http.get(api_url, allow_redirects=False, raise_for_status=False)
            if res.status_code == 302:
                stream_url = res.headers.get("Location")
                return HLSStream.parse_variant_playlist(self.session, stream_url, headers={
                    "Referer": self.url
                })
            else:
                error = self.session.http.json(res)
                self.logger.error("{0}: {1}",
                                  error.get("title", "Error"),
                                  error.get("description", "An unknown error occurred"))


__plugin__ = ThePlatform
