#-plugin-sig:PgyacPgUCu5Wew9XexwI3W8y0YC3Vq/sPxYzGJ/4MMNY8TkN1v9ox54cfuraX5VQ7X53Wm5xt8fscqVtBH+1Bbx1IBNXtxPs14+HGUltoX6KGISOd3CPy2dFGA7qK/zUUvc6GqAVuOz7p7BwLbto54y8b6VulPzxSQ8EfCJlvmTTNhWw9YZ7hJFgn2Kxk6rxy2OaVAzXHAi8+FsLNTI3enW0mHuqOIeujh/GE2HxfMgFAskOzFtBCRZhfQ2x97p0EIYedxEjvfyAvJC2onaaSivT+/dG0TZnY0WsSOCPwE40/jFFvz+zxzUUyG8mFHufYJlqzahnC1G+ODkKp5vK7A==
import base64
import json
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HDSStream, HLSStream


def jwt_decode(token):
    info, payload, sig = token.split(".")
    data = base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4))
    return json.loads(data)


class PlayTV(Plugin):
    FORMATS_URL = 'https://playtv.fr/player/initialize/{0}/'
    API_URL = 'https://playtv.fr/player/play/{0}/?format={1}&language={2}&bitrate={3}'

    _url_re = re.compile(r'https?://(?:playtv\.fr/television|(:?\w+\.)?play\.tv/live-tv/\d+)/(?P<channel>[^/]+)/?')

    _formats_schema = validate.Schema({
        'streams': validate.any(
            [],
            {
                validate.text: validate.Schema({
                    validate.text: {
                        'bitrates': validate.all([
                            validate.Schema({
                                'value': int
                            })
                        ])
                    }
                })
            }
        )
    })

    _api_schema = validate.Schema(
        validate.transform(lambda x: jwt_decode(x)),
        {
            'url': validate.url()
        }
    )

    @classmethod
    def can_handle_url(cls, url):
        return PlayTV._url_re.match(url)

    def _get_streams(self):
        match = self._url_re.match(self.url)
        channel = match.group('channel')

        res = self.session.http.get(self.FORMATS_URL.format(channel))
        streams = self.session.http.json(res, schema=self._formats_schema)['streams']
        if streams == []:
            self.logger.error('Channel may be geo-restricted, not directly provided by PlayTV or not freely available')
            return

        for language in streams:
            for protocol, bitrates in list(streams[language].items()):
                # - Ignore non-supported protocols (RTSP, DASH)
                # - Ignore deprecated Flash (RTMPE/HDS) streams (PlayTV doesn't provide anymore a Flash player)
                if protocol in ['rtsp', 'flash', 'dash', 'hds']:
                    continue

                for bitrate in bitrates['bitrates']:
                    if bitrate['value'] == 0:
                        continue
                    api_url = self.API_URL.format(channel, protocol, language, bitrate['value'])
                    res = self.session.http.get(api_url)
                    video_url = self._api_schema.validate(res.text)['url']
                    bs = '{0}k'.format(bitrate['value'])

                    if protocol == 'hls':
                        for _, stream in HLSStream.parse_variant_playlist(self.session, video_url).items():
                            yield bs, stream
                    elif protocol == 'hds':
                        for _, stream in HDSStream.parse_manifest(self.session, video_url).items():
                            yield bs, stream


__plugin__ = PlayTV
