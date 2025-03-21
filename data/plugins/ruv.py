#-plugin-sig:l016N8nqhfx82yb6uA3HJu6jJn0qpo6PP81XL1AmXBtAQUbZO3XjZq1RtQ/pW0Lr9jmUoDlKBjDpDWLXYEbkcvld/51vdw5br468HxxUUS7ccbKWiOrbl0FFk8fZ/XbOHEV/Nei+XoEQqYZQNW9v2N4sURALCaBA/eMg2fzdZa/JkzX6c5hpTj9cI6cyONkrekGquQ5gCyw6u1I1VfNKM47fW5TiLMJ+coy6XUyOGoIu9EtKLpbsnzxWDjXK8+2St97s6Co0WZF/kze5myAJkxS1G1BipV79Rp+AZhrgQXkEamA2PxziV4TzEwAQuGMzJrlWF1zxWY0Ik+/yl76oTA==
"""Plugin for RUV, the Icelandic national television."""

import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

# URL to the RUV LIVE API
RUV_LIVE_API = """http://www.ruv.is/sites/all/themes/at_ruv/scripts/\
ruv-stream.php?channel={0}&format=json"""


_live_url_re = re.compile(r"""^(?:https?://)?(?:www\.)?ruv\.is/
                                (?P<stream_id>
                                    ruv/?$|
                                    ruv2/?$|
                                    ruv-2/?$|
                                    ras1/?$|
                                    ras2/?$|
                                    rondo/?$
                                )
                                /?
                                """, re.VERBOSE)

_sarpurinn_url_re = re.compile(r"""^(?:https?://)?(?:www\.)?ruv\.is/spila/
                                    (?P<stream_id>
                                        ruv|
                                        ruv2|
                                        ruv-2|
                                        ruv-aukaras|
                                    )
                                    /
                                    [a-zA-Z0-9_-]+
                                    /
                                    [0-9]+
                                    /?
                                    """, re.VERBOSE)

_single_re = re.compile(r"""(?P<url>http://[0-9a-zA-Z\-\.]*/
                            (lokad|opid)
                            /
                            ([0-9]+/[0-9][0-9]/[0-9][0-9]/)?
                            ([A-Z0-9\$_]+\.mp4\.m3u8)
                            )
                         """, re.VERBOSE)

_multi_re = re.compile(r"""(?P<base_url>http://[0-9a-zA-Z\-\.]*/
                            (lokad|opid)
                            /)
                            manifest.m3u8\?tlm=hls&streams=
                            (?P<streams>[0-9a-zA-Z\/\.\,:]+)
                         """, re.VERBOSE)


class Ruv(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _live_url_re.match(url) or _sarpurinn_url_re.match(url)

    def __init__(self, url):
        Plugin.__init__(self, url)
        live_match = _live_url_re.match(url)

        if live_match:
            self.live = True
            self.stream_id = live_match.group("stream_id")

            # Remove slashes
            self.stream_id.replace("/", "")

            # Remove dashes
            self.stream_id.replace("-", "")

            # Rondo is identified as ras3
            if self.stream_id == "rondo":
                self.stream_id = "ras3"
        else:
            self.live = False

    def _get_live_streams(self):
        # Get JSON API
        res = self.session.http.get(RUV_LIVE_API.format(self.stream_id))

        # Parse the JSON API
        json_res = self.session.http.json(res)

        for url in json_res["result"]:
            if url.startswith("rtmp:"):
                continue

            # Get available streams
            streams = HLSStream.parse_variant_playlist(self.session, url)

            for quality, hls in streams.items():
                yield quality, hls

    def _get_sarpurinn_streams(self):
        # Get HTML page
        res = self.session.http.get(self.url).text
        lines = "\n".join([line for line in res.split("\n") if "video.src" in line])
        multi_stream_match = _multi_re.search(lines)

        if multi_stream_match and multi_stream_match.group("streams"):
            base_url = multi_stream_match.group("base_url")
            streams = multi_stream_match.group("streams").split(",")

            for stream in streams:
                if stream.count(":") != 1:
                    continue

                [token, quality] = stream.split(":")
                quality = int(quality)
                key = ""

                if quality <= 500:
                    key = "240p"
                elif quality <= 800:
                    key = "360p"
                elif quality <= 1200:
                    key = "480p"
                elif quality <= 2400:
                    key = "720p"
                else:
                    key = "1080p"

                yield key, HLSStream(
                    self.session,
                    base_url + token
                )

        else:
            single_stream_match = _single_re.search(lines)

            if single_stream_match:
                url = single_stream_match.group("url")
                yield "576p", HLSStream(self.session, url)

    def _get_streams(self):
        if self.live:
            return self._get_live_streams()
        else:
            return self._get_sarpurinn_streams()


__plugin__ = Ruv
