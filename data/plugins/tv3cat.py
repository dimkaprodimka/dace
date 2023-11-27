#-plugin-sig:iyk77RH1+SDPir3d3PanRbiq4BW5oBI8f3Ly1GOffptLQra+Tuiyid33hMo4nhRN2L1ER1FHOTGyDkXIVSbiR5sa2SnI8xxGL9qYMj4YI7AyXjOeAYGLzGNwq1DZMvHycYLeLbL+sgb2zh8q/3WTigifglHwFSD1RHSanggJWmNfCGL7NWny42MqOE3dBcdxsPXCnV2ymrqmCQGFW9Jxd0la1Si+S+dZ8gANKpEhI4HYHpE0kEE11DwHFoCe2cA58DjriDp1bcOHzgKA96WdlM56YXyCk+57iTBrWRpC1NSm8kSCanpH+Dnkuwbuee0CUfrqZW4hIKz0pjdYjtftHQ==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin, PluginError
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.plugin.api import validate

log = logging.getLogger(__name__)


class TV3Cat(Plugin):
    _url_re = re.compile(r"http://(?:www.)?ccma.cat/tv3/directe/(.+?)/")
    _stream_info_url = "http://dinamics.ccma.cat/pvideo/media.jsp" \
                       "?media=video&version=0s&idint={ident}&profile=pc&desplacament=0"
    _media_schema = validate.Schema({
        "geo": validate.text,
        "url": validate.url(scheme=validate.any("http", "https"))
    })
    _channel_schema = validate.Schema({
        "media": validate.any([_media_schema], _media_schema)},
        validate.get("media"),
        # If there is only one item, it's not a list ... silly
        validate.transform(lambda x: x if isinstance(x, list) else [x])
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        match = self._url_re.match(self.url)
        if match:
            ident = match.group(1)
            data_url = self._stream_info_url.format(ident=ident)
            stream_infos = self.session.http.json(self.session.http.get(data_url), schema=self._channel_schema)

            for stream in stream_infos:
                try:
                    return HLSStream.parse_variant_playlist(self.session, stream['url'], name_fmt="{pixels}_{bitrate}")
                except PluginError:
                    log.debug("Failed to get streams for: {0}".format(stream['geo']))
                    pass


__plugin__ = TV3Cat
