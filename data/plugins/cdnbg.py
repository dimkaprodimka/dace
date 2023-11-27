#-plugin-sig:lU7aMwg1Kt0x0N47ixuuS2aciygFIK9183FBhya9d3Ft3mZR1zxOeBNO+XW+iXCIXElrZ4L6N1tmke/7nPOKGkJY+QYac6qP8I35FHEPFNdc1iah9XTokKMulhREfyCuN8+PQeWrMSVx7SB/Ws+f9yOUCuhMZUODn9V98bYDn918i8fWA68Vgwz4gGl8mmgRhajUoJDXjDwTB+ZksRW/T1I2ZBc63gT4eXBQsVLd3Xq8Ag/+52j6Ade0mwbjdKLL1jkeNfJ5M4BSGCXUxWUoI8EoGQSmKusEHsvjR8eqWC/7cjaCFEIW8kGYIMjCAFuYcwIljb+cRZBAe0gmMHmWWw==
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import urlparse
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import update_scheme

log = logging.getLogger(__name__)


class CDNBG(Plugin):
    url_re = re.compile(r"""
        https?://(?:www\.)?(?:
            tv\.bnt\.bg/\w+(?:/\w+)?|
            nova\.bg/live|
            bgonair\.bg/tvonline|
            mmtvmusic\.com/live|
            mu-vi\.tv/LiveStreams/pages/Live\.aspx|
            live\.bstv\.bg|
            bloombergtv.bg/video|
            armymedia.bg|
            chernomore.bg|
            i.cdn.bg/live/
        )/?
    """, re.VERBOSE)
    iframe_re = re.compile(r"iframe .*?src=\"((?:https?(?::|&#58;))?//(?:\w+\.)?cdn.bg/live[^\"]+)\"", re.DOTALL)
    sdata_re = re.compile(r"sdata\.src.*?=.*?(?P<q>[\"'])(?P<url>http.*?)(?P=q)")
    hls_file_re = re.compile(r"(src|file): (?P<q>[\"'])(?P<url>(https?:)?//.+?m3u8.*?)(?P=q)")
    hls_src_re = re.compile(r"video src=(?P<url>http[^ ]+m3u8[^ ]*)")

    stream_schema = validate.Schema(
        validate.any(
            validate.all(validate.transform(sdata_re.search), validate.get("url")),
            validate.all(validate.transform(hls_file_re.search), validate.get("url")),
            validate.all(validate.transform(hls_src_re.search), validate.get("url")),
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def find_iframe(self, url):
        self.session.http.headers.update({"User-Agent": useragents.CHROME})
        res = self.session.http.get(self.url)
        p = urlparse(url)
        for iframe_url in self.iframe_re.findall(res.text):
            if "googletagmanager" not in iframe_url:
                log.debug("Found iframe: {0}", iframe_url)
                iframe_url = iframe_url.replace("&#58;", ":")
                if iframe_url.startswith("//"):
                    return "{0}:{1}".format(p.scheme, iframe_url)
                else:
                    return iframe_url

    def _get_streams(self):
        if "i.cdn.bg/live/" in self.url:
            iframe_url = self.url
        else:
            iframe_url = self.find_iframe(self.url)

        if iframe_url:
            res = self.session.http.get(iframe_url, headers={"Referer": self.url})
            stream_url = update_scheme(self.url, self.stream_schema.validate(res.text))
            log.warning("SSL Verification disabled.")
            return HLSStream.parse_variant_playlist(self.session,
                                                    stream_url,
                                                    verify=False)


__plugin__ = CDNBG
