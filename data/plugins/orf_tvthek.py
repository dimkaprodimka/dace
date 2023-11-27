#-plugin-sig:QwB1DY3Dv+XL7R2zpfrgQI3ZpmPle5GNdjWZ2I56x644wUonB9rF2VRuDTNZYntmD6xx+EtUE70hCEtNVVS+TrUeYtd/1McMgikoIJVh/q9AngmLdQRNg1R7agnrVh/UXJ9FiBccuTTj10ApcGsN+UfeR44rUOY+5kb4gbjK7pxgmqIz+EQlKYk2kbzmOddm2enDpu+fFVvmlXMIHPQExH5n83oKntaGycvvOPy1s+wBMtgg6eH98C1Evrc8OGKThOOz2FT03AIXPz6zLT5AN9hlKFLj9aDm088HcDYxYyiuaowvSXrClyS48bfpNt8M4kc6AcAdoQEH0vwxpvasOg==
import re
import json

from ACEStream.PluginsContainer.streamlink.plugin import Plugin, PluginError
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

_stream_url_re = re.compile(r'https?://tvthek\.orf\.at/(index\.php/)?live/(?P<title>[^/]+)/(?P<id>[0-9]+)')
_vod_url_re = re.compile(r'''
    https?://tvthek\.orf\.at/pro(gram|file)
    /(?P<showtitle>[^/]+)/(?P<showid>[0-9]+)
    /(?P<episodetitle>[^/]+)/(?P<epsiodeid>[0-9]+)
    (/(?P<segmenttitle>[^/]+)/(?P<segmentid>[0-9]+))?
''', re.VERBOSE)
_json_re = re.compile(r'<div class="jsb_ jsb_VideoPlaylist" data-jsb="(?P<json>[^"]+)">')

MODE_STREAM, MODE_VOD = 0, 1


class ORFTVThek(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _stream_url_re.match(url) or _vod_url_re.match(url)

    def _get_streams(self):
        if _stream_url_re.match(self.url):
            mode = MODE_STREAM
        else:
            mode = MODE_VOD

        res = self.session.http.get(self.url)
        match = _json_re.search(res.text)
        if match:
            data = json.loads(_json_re.search(res.text).group('json').replace('&quot;', '"'))
        else:
            raise PluginError("Could not extract JSON metadata")

        streams = {}
        try:
            if mode == MODE_STREAM:
                sources = data['playlist']['videos'][0]['sources']
            elif mode == MODE_VOD:
                sources = data['selected_video']['sources']
        except (KeyError, IndexError):
            raise PluginError("Could not extract sources")

        for source in sources:
            try:
                if source['delivery'] != 'hls':
                    continue
                url = source['src'].replace(r'\/', '/')
            except KeyError:
                continue
            stream = HLSStream.parse_variant_playlist(self.session, url)
            # work around broken HTTP connection persistence by acquiring a new connection
            self.session.http.close()
            streams.update(stream)

        return streams


__plugin__ = ORFTVThek
