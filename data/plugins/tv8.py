#-plugin-sig:baWxecLKGntesgDfS29oSiODhfbROL99drOVnnNPbijD2ZhDVreakHvLEMs8nPfl7huAjl0wkqBjBhO8SOcARg88M51wVXfDwLQ5o3ArclKbVphDkKFzWkq4lCPyohXFJ/BQzgG/vbVlWlQ6GhG7NcsEDiK+BURqUzRpsZwXBNO247txOPkJujPrOTCtW3/6NWzR42pSr+An3TJlcVX12OyhTI9YEenvqLWNNH+cnPIbZ3S6Lk0ivHxGLs3ntdsqD9rKdUc+jiZ/r6QSb8ICsZucGPSpG1dGNnU6N/89Aw1swhj4IOaAbDeZmFuISCDY8ZNz1wGFGk94DmdfET5RdA==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class TV8(Plugin):
    _url_re = re.compile(r'https?://www\.tv8\.com\.tr/canli-yayin')
    _player_schema = validate.Schema(validate.all({
        'servers': {
            validate.optional('manifest'): validate.url(),
            'hlsmanifest': validate.url(),
        }},
        validate.get('servers')))

    API_URL = 'https://static.personamedia.tv/player/config/tv8.json'

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def get_title(self):
        return 'TV8'

    def _get_streams(self):
        res = self.session.http.get(self.API_URL)
        data = self.session.http.json(res, schema=self._player_schema)
        log.debug('{0!r}'.format(data))
        return HLSStream.parse_variant_playlist(self.session, data['hlsmanifest'])


__plugin__ = TV8
