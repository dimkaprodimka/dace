#-plugin-sig:nWcM4AuRBVxrsFcjVldnZer6crHLbyI5DQYhLBJvuIQwHnfgBR2rA4oIEGyeqbIx/VCqt2plT2Dssy1ssllf0P0ctOv9TWZ4zANmt70Zeh8q63E9RE2ocdj58lIseg4J170QsMe1quHBHpn2BvEEZt8VGMPfjYxFdTHj46SMpaYLAGPv5bNYeHp7l3EjzO4zLG+iBbTK24bEbDIB5n54UqcoZ2kXBma/LAsC14TvhWSKEPVJcmnTE0U6ie3d8RoxlwS4bex0TxtYM0LAqImnCI0zCq1TsbIhBmF9RMDwe8XKGKIPmiJUxtb/cHlmTyU0hhQOgR9/gzRtLl+JO5Vrxg==
import re
import logging

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import itertags
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.compat import urlparse, parse_qsl

log = logging.getLogger(__name__)


class SenateGov(Plugin):
    url_re = re.compile(r"""https?://(?:.+\.)?senate\.gov/(isvp)?""")
    streaminfo_re = re.compile(r"""var\s+streamInfo\s+=\s+new\s+Array\s*\(\s*(\[.*\])\);""")
    stt_re = re.compile(r"""^(?:(?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+)$""")
    url_lookup = {
        "ag": ["76440", "https://ag-f.akamaihd.net"],
        "aging": ["76442", "https://aging-f.akamaihd.net"],
        "approps": ["76441", "https://approps-f.akamaihd.net"],
        "armed": ["76445", "https://armed-f.akamaihd.net"],
        "banking": ["76446", "https://banking-f.akamaihd.net"],
        "budget": ["76447", "https://budget-f.akamaihd.net"],
        "cecc": ["76486", "https://srs-f.akamaihd.net"],
        "commerce": ["80177", "https://commerce1-f.akamaihd.net"],
        "csce": ["75229", "https://srs-f.akamaihd.net"],
        "dpc": ["76590", "https://dpc-f.akamaihd.net"],
        "energy": ["76448", "https://energy-f.akamaihd.net"],
        "epw": ["76478", "https://epw-f.akamaihd.net"],
        "ethics": ["76449", "https://ethics-f.akamaihd.net"],
        "finance": ["76450", "https://finance-f.akamaihd.net"],
        "foreign": ["76451", "https://foreign-f.akamaihd.net"],
        "govtaff": ["76453", "https://govtaff-f.akamaihd.net"],
        "help": ["76452", "https://help-f.akamaihd.net"],
        "indian": ["76455", "https://indian-f.akamaihd.net"],
        "intel": ["76456", "https://intel-f.akamaihd.net"],
        "intlnarc": ["76457", "https://intlnarc-f.akamaihd.net"],
        "jccic": ["85180", "https://jccic-f.akamaihd.net"],
        "jec": ["76458", "https://jec-f.akamaihd.net"],
        "judiciary": ["76459", "https://judiciary-f.akamaihd.net"],
        "rpc": ["76591", "https://rpc-f.akamaihd.net"],
        "rules": ["76460", "https://rules-f.akamaihd.net"],
        "saa": ["76489", "https://srs-f.akamaihd.net"],
        "smbiz": ["76461", "https://smbiz-f.akamaihd.net"],
        "srs": ["75229", "https://srs-f.akamaihd.net"],
        "uscc": ["76487", "https://srs-f.akamaihd.net"],
        "vetaff": ["76462", "https://vetaff-f.akamaihd.net"],
    }

    hls_url = "{base}/i/{filename}_1@{number}/master.m3u8?"
    hlsarch_url = "https://ussenate-f.akamaihd.net/i/{filename}.mp4/master.m3u8"

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _isvp_to_m3u8(self, url):
        qs = dict(parse_qsl(urlparse(url).query))
        if "comm" not in qs:
            log.error("Missing `comm` value")
        if "filename" not in qs:
            log.error("Missing `filename` value")

        d = self.url_lookup.get(qs['comm'])
        if d:
            snumber, baseurl = d
            stream_url = self.hls_url.format(filename=qs['filename'], number=snumber, base=baseurl)
        else:
            stream_url = self.hlsarch_url.format(filename=qs['filename'])

        return stream_url, self.parse_stt(qs.get('stt', 0))

    def _get_streams(self):
        self.session.http.headers.update({
            "User-Agent": useragents.CHROME,
        })
        m = self.url_re.match(self.url)
        if m and not m.group(1):
            log.debug("Searching for ISVP URL")
            isvp_url = self._get_isvp_url()
        else:
            isvp_url = self.url

        if not isvp_url:
            log.error("Could not find the ISVP URL")
            return
        else:
            log.debug("ISVP URL: {0}".format(isvp_url))

        stream_url, start_offset = self._isvp_to_m3u8(isvp_url)
        log.debug("Start offset is: {0}s".format(start_offset))
        return HLSStream.parse_variant_playlist(self.session, stream_url, start_offset=start_offset)

    def _get_isvp_url(self):
        res = self.session.http.get(self.url)
        for iframe in itertags(res.text, 'iframe'):
            m = self.url_re.match(iframe.attributes.get('src'))
            return m and m.group(1) is not None and iframe.attributes.get('src')

    @classmethod
    def parse_stt(cls, param):
        m = cls.stt_re.match(param)
        if not m:
            return 0
        return (
            int(m.group('hours') or 0) * 3600
            + int(m.group('minutes')) * 60
            + int(m.group('seconds'))
        )


__plugin__ = SenateGov
