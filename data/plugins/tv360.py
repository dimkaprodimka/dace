#-plugin-sig:AN+8sQNVpcfY5FlLfbVQ28J06/HjJvn1scQJG41+rFFGMAs14Uj2Sgj232+ePtbnifR1HHevEpKJHJoiCCjf54ZG47ZYC9rCE1BYhBdx3eY5pQ/8zkTJuuHD/qG/Ggt8D7/PBEFQ/SRAb0DAbFYwAtiuHgU2mZ3FcRnE2z6sLbur3Q22QqfzBy1mnmx/ktCCjhhDYFRZ4qhxcx4mnL4w0ncYTqXnfmE9qD1MUreUNl4NZxPy4dF/kCtp6DCbKcVHfPAbp7QOPhEL2lbKoghDDoG3f/K/vPKvCQmWkU6BH+7VreofxAemruor7oFl9ITC1u569M0vLpqmkmV4EqU8ZQ==
from __future__ import print_function

import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class TV360(Plugin):
    url_re = re.compile(r"https?://(?:www.)?tv360.com.tr/canli-yayin")
    hls_re = re.compile(r'''hls.loadSource\(["'](http.*m3u8)["']\)''', re.DOTALL)

    hls_schema = validate.Schema(
        validate.transform(hls_re.search),
        validate.any(None, validate.all(validate.get(1)))
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        hls_url = self.hls_re.search(res.text)

        if hls_url:
            return HLSStream.parse_variant_playlist(self.session, hls_url.group(1))


__plugin__ = TV360
