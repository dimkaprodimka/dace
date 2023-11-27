#-plugin-sig:aoEr+Kda2SbqkJ4tURLtCPDiDc6kKnJ1JjsvEbjbnqJPBaxvFeyLoeplprLuuFoDKH5FyzjgVVRZn3gArNRJlWZmiZGUwDgunzcvCRVoUMscN18soo14Nxbqkiuy2d5DCfghm98/RRd8erk5Wyx/4WXe8VGGlUXjt0e82I3U823c06LjGXGV+bEqqzP8FpT16WUSyNNyl9LD5Qhm3KLcRf+GnD1z+nQQii0qZmZbTtxntd+sPL3FAL7Paq72GO65vHMFpUVuMst2rdcL+iujTOIU5KRSgJARb13I5x81+tVJ5kAdZxoy8TDUYGRHBL7DExu5QSskfi5mW9qdvI9jBA==
from __future__ import print_function
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HDSStream
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class TRTSpor(Plugin):
    """
    Support for trtsport.com a Turkish Sports Broadcaster
    """
    url_re = re.compile(r"https?://(?:www.)?trtspor.com/canli-yayin-izle/.+/?")
    f4mm_re = re.compile(r'''(?P<q>["'])(?P<url>http[^"']+?.f4m)(?P=q),''')
    m3u8_re = re.compile(r'''(?P<q>["'])(?P<url>http[^"']+?.m3u8)(?P=q),''')

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        url_m = self.m3u8_re.search(res.text)
        hls_url = url_m and url_m.group("url")
        if hls_url:
            for s in HLSStream.parse_variant_playlist(self.session, hls_url).items():
                yield s

        f4m_m = self.f4mm_re.search(res.text)
        f4m_url = f4m_m and f4m_m.group("url")
        if f4m_url:
            for n, s in HDSStream.parse_manifest(self.session, f4m_url).items():
                yield n, s


__plugin__ = TRTSpor
