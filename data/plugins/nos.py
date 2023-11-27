#-plugin-sig:TwgTxfLKVNSp4uqcSeDEB5BJRVoPwTPyrTqamt0J0uX8R17rMMvYKMc70mDE2R5QjzW5MfI55KIfbSrE7+Jm8AUx2wRn+9nq4nxmGMx7vjuMsK8O54hZUaJ9sX/rezwXLSoMP9nKYc/F7CDP4Ca1bw1VAeuEH0XQdSrJBPTM9ehUMgtIaUkbn9/anFQVFWZhTqqVlyIpaNDBpJFdI3oUI8TRnnYNta67GZVsLuf9H0+m6KJm/ZsO89QMiy+zG6zbMCPmRcAP+odv4bpXACtq7VEayreLOhMew3eifjhWKOFtPcMVISRaglTSq/5DwdaBht5wFEu10O0jfQv4Jo+ObA==
"""Plugin for NOS: Nederlandse Omroep Stichting

Supports:
   MP$: http://nos.nl/uitzending/nieuwsuur.html
   Live: http://www.nos.nl/livestream/*
   Tour: http://nos.nl/tour/live
"""
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import urljoin
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import itertags
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class NOS(Plugin):
    _url_re = re.compile(r"https?://(?:\w+\.)?nos.nl/")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _resolve_stream(self):
        res = self.session.http.get(self.url)
        for video in itertags(res.text, 'video'):
            stream_url = video.attributes.get("data-stream")
            log.debug("Stream data: {0}".format(stream_url))
            return HLSStream.parse_variant_playlist(self.session, stream_url)

    def _get_source_streams(self):
        res = self.session.http.get(self.url)

        for atag in itertags(res.text, 'a'):
            if "video-play__link" in atag.attributes.get("class", ""):
                href = urljoin(self.url, atag.attributes.get("href"))
                log.debug("Loading embedded video page")
                vpage = self.session.http.get(href, params=dict(ajax="true", npo_cc_skip_wall="true"))
                for source in itertags(vpage.text, 'source'):
                    return HLSStream.parse_variant_playlist(self.session, source.attributes.get("src"))

    def _get_streams(self):
        if "/livestream/" in self.url or "/tour/" in self.url:
            log.debug("Finding live streams")
            return self._resolve_stream()
        else:
            log.debug("Finding VOD streams")
            return self._get_source_streams()


__plugin__ = NOS
