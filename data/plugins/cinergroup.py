#-plugin-sig:Q9BLJS4JQ5Rb5B7ub5LYEl63n8gTXaNF5HCScfRD+ljivlaQVi9AsEGenYfzWcBi87CBL1qC7i8BjHJeAjrXaQAK3usN+EyOaml0kLN4xpO4DgW6JL0N8nl9PN32QRJBRjA1UyLvSAz6fllOAq9TsdseHHGwuTsQ1c4Ww+KniPJwVOI9iufXQmZw186SaiRwTYEKHnfzlNLPNTpMHkFDX/8GKIxOt0MvdWLQnMhmFjB1ePEwLf38bXL148SByyCsNiosz9lMi82lgeDOmpbewOh61Dd2QAGc4CV8n6XZDmkTdSufF4pl6eNTbX3TJcuGK949lhVDMoZ33g3Bugb8NQ==
from __future__ import print_function

import json
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.compat import unquote


class CinerGroup(Plugin):
    """
    Support for the live stream on www.showtv.com.tr
    """
    url_re = re.compile(r"""https?://(?:www.)?
        (?:
            showtv.com.tr/canli-yayin(/showtv)?|
            haberturk.com/canliyayin|
            haberturk.com/tv/canliyayin|
            showmax.com.tr/canliyayin|
            showturk.com.tr/canli-yayin/showturk|
            bloomberght.com/tv|
            haberturk.tv/canliyayin
        )/?""", re.VERBOSE)
    stream_re = re.compile(r"""div .*? data-ht=(?P<quote>["'])(?P<data>.*?)(?P=quote)""", re.DOTALL)
    stream_data_schema = validate.Schema(
        validate.transform(stream_re.search),
        validate.any(
            None,
            validate.all(
                validate.get("data"),
                validate.transform(unquote),
                validate.transform(lambda x: x.replace("&quot;", '"')),
                validate.transform(json.loads),
                {
                    "ht_stream_m3u8": validate.url()
                },
                validate.get("ht_stream_m3u8")
            )
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        stream_url = self.stream_data_schema.validate(res.text)
        if stream_url:
            return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = CinerGroup
