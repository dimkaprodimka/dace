#-plugin-sig:VdoPS6ojwItGphQ0G1BEGPkWFpAAW9hewF14fYIfMGHqbO7A05lPUDCjHIie4AucvD2CzAq4xtQzSbIZx+1Z+nzC9ds3xn2O+U2bdv63WsTvOUsgbJ66LXHvVki2H30HsYfHvirQ63LIc3Jl9E7kmFcjGvrCN/YpX0KhH/wkWxVDInzuSCulXiQgxCpxyF1FHqCK8WWZ2Lx2t2iqmo6dBL/UgkQXrSE+0Ykg4bhNuavR/+C4vwRXENUKQ89ESYRyJpwt1bD5nYPlEv6iL3NdQGv133fXwqy6SNnOfCU40VV1v98Xkq2gMNfbLD1X5TkAAKZzEYVGta96pQ4TeESv1g==
import re
import logging

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import itertags
from ACEStream.PluginsContainer.streamlink.plugin.api.support_plugin import youtube
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import update_scheme

YouTube = youtube.YouTube
log = logging.getLogger(__name__)


class Dogus(Plugin):
    """
    Support for live streams from Dogus sites include ntv, ntvspor, and kralmuzik
    """

    url_re = re.compile(r"""https?://(?:www.)?
        (?:
            ntv.com.tr/canli-yayin/ntv|
            ntvspor.net/canli-yayin|
            kralmuzik.com.tr/tv/|
            eurostartv.com.tr/canli-izle
        )/?""", re.VERBOSE)
    mobile_url_re = re.compile(r"""(?P<q>["'])(?P<url>(https?:)?//[^'"]*?/live/hls/[^'"]*?\?token=)
                                   (?P<token>[^'"]*?)(?P=q)""", re.VERBOSE)
    token_re = re.compile(r"""token=(?P<q>["'])(?P<token>[^'"]*?)(?P=q)""")
    kral_token_url = "https://service.kralmuzik.com.tr/version/gettoken"

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)

        # Look for Youtube embedded video first
        for iframe in itertags(res.text, 'iframe'):
            if YouTube.can_handle_url(iframe.attributes.get("src")):
                log.debug("Handing off to YouTube plugin")
                return self.session.streams(iframe.attributes.get("src"))

        # Next check for HLS URL with token
        mobile_url_m = self.mobile_url_re.search(res.text)
        mobile_url = mobile_url_m and update_scheme(self.url, mobile_url_m.group("url"))
        if mobile_url:
            log.debug("Found mobile stream: {0}".format(mobile_url_m.group(0)))

            token = mobile_url_m and mobile_url_m.group("token")
            if not token and "kralmuzik" in self.url:
                log.debug("Getting Kral Muzik HLS stream token from API")
                token = self.session.http.get(self.kral_token_url).text
            elif not token:
                # if no token is in the url, try to find it else where in the page
                log.debug("Searching for HLS stream token in URL")
                token_m = self.token_re.search(res.text)
                token = token_m and token_m.group("token")

            return HLSStream.parse_variant_playlist(self.session, mobile_url + token,
                                                    headers={"Referer": self.url})


__plugin__ = Dogus
