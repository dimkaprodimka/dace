#-plugin-sig:Ax2/1PStMXC/D6iY7wBiVSNsVayKBroPiTqit3XsyJq+7yB+5rSKtDDVzeoti1WemXfTFPYiNSBO5xXhVvXA8MEKDZjjwZ5F1OA7Nxq5mbPfLXKUjHu0mkT7wFbfT40z9lVpvj4JAMJ06SlJ1Ud4bFU+6JLLi6bJuAs+BZPkr3H5Z4FFawQzhYbxRzsWRhggMrC3WCNsK6Xfr7N88wjrk0nMLvxnEB+Sc6KAd1AoKUqJYOpiaIkx/0E5f9nTCMjtvBFmRumpg4FsvtMaMSI6pNg9oUTs45qJspXK9almMdc1DOxRW4QakPvZk+q1gpoYln8rFpUuGIxhYmlpMqdL2A==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream, HTTPStream, RTMPStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json
from ACEStream.PluginsContainer.streamlink.plugin.api.support_plugin import common_jwplayer

_js_to_json = common_jwplayer._js_to_json

class TV5Monde(Plugin):
    _url_re = re.compile(r'http://(.+\.)?(tv|tivi)5monde(plus(afrique)?)?\.com')
    _videos_re = re.compile(r'"?(?:files|sources)"?:\s*(?P<videos>\[.+?\])')
    _videos_embed_re = re.compile(r'(?:file:\s*|src=)"(?P<embed>.+?\.mp4|.+?/embed/.+?)"')

    _videos_schema = validate.Schema(
        validate.transform(_js_to_json),
        validate.transform(parse_json),
        validate.all([
            validate.any(
                validate.Schema(
                    {'url': validate.url()},
                    validate.get('url')
                ),
                validate.Schema(
                    {'file': validate.url()},
                    validate.get('file')
                ),
            )
        ])
    )

    @classmethod
    def can_handle_url(cls, url):
        return TV5Monde._url_re.match(url)

    def _get_non_embed_streams(self, page):
        match = self._videos_re.search(page)
        if match is not None:
            videos = self._videos_schema.validate(match.group('videos'))
            return videos

        return []

    def _get_embed_streams(self, page):
        match = self._videos_embed_re.search(page)
        if match is None:
            return []

        url = match.group('embed')
        if '.mp4' in url:
            return [url]

        res = self.session.http.get(url)
        videos = self._get_non_embed_streams(res.text)
        if videos:
            return videos

        return []

    def _get_streams(self):
        res = self.session.http.get(self.url)
        match = self._videos_re.search(res.text)
        if match is not None:
            videos = self._videos_schema.validate(match.group('videos'))
        else:
            videos = self._get_embed_streams(res.text)

        for url in videos:
            if '.m3u8' in url:
                for stream in HLSStream.parse_variant_playlist(self.session, url).items():
                    yield stream
            elif 'rtmp' in url:
                yield 'vod', RTMPStream(self.session, {'rtmp': url})
            elif '.mp4' in url:
                yield 'vod', HTTPStream(self.session, url)


__plugin__ = TV5Monde
