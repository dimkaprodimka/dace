#-plugin-sig:hUEMNUhVph7lt6n9RnK22swtH7wM9GwDEpYqql48Iese2jdpcpu1T7tcazn354hZrZAeXf5AvuhUOZW0Umvgf8P+j9UFRhzJgfqtbXUSanLUjo/mbR/PZ23lXY2ZbOGacYHwXrtUAV+PGoWzj25TUo/NE0o/huNa6o5cB8aMboiNM/3O+EPzi3hpgh/HJTKHL4RLYRlrrr1mPnT6pSfLuVQefrAUWcLOAvv1ybwiCJ7aebk35HDLV7CyJa7SfhueaxXSjaJ3Rqyqu+TBLNLfr1Smcs6rb5ZAm+KpDc3tRh83HtdFRXRzs4Xk1aY8RxPYt7sI6URFotvL7oOXBdHmdA==
import re
from time import time
import logging
import json

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.compat import urlparse, urljoin

log = logging.getLogger(__name__)


class OlympicChannel(Plugin):
    _url_re = re.compile(r"https?://(\w+\.)olympicchannel.com/../(?P<type>live|video|original-series|films)/?(?:\w?|[-\w]+)")
    _tokenizationApiDomainUrl = """"tokenizationApiDomainUrl" content="/OcsTokenization/api/v1/tokenizedUrl">"""
    _live_api_path = "/OcsTokenization/api/v1/tokenizedUrl?url={url}&domain={netloc}&_ts={time}"

    _api_schema = validate.Schema(
        validate.text,
        validate.transform(lambda v: json.loads(v)),
        validate.url()
    )
    _video_url_re = re.compile(r""""video_url"\scontent\s*=\s*"(?P<value>[^"]+)""")
    _video_url_schema = validate.Schema(
        validate.contains(_tokenizationApiDomainUrl),
        validate.transform(_video_url_re.search),
        validate.any(None, validate.get("value")),
        validate.url()
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_vod_streams(self):
        stream_url = self.session.http.get(self.url, schema=self._video_url_schema)
        return HLSStream.parse_variant_playlist(self.session, stream_url)

    def _get_live_streams(self):
        video_url = self.session.http.get(self.url, schema=self._video_url_schema)
        parsed = urlparse(video_url)
        api_url = urljoin(self.url, self._live_api_path.format(url=video_url,
                          netloc="{0}://{1}".format(parsed.scheme, parsed.netloc), time=int(time())))
        stream_url = self.session.http.get(api_url, schema=self._api_schema)
        return HLSStream.parse_variant_playlist(self.session, stream_url)

    def _get_streams(self):
        match = self._url_re.match(self.url)
        type_of_stream = match.group('type')

        if type_of_stream == 'live':
            return self._get_live_streams()
        elif type_of_stream in ('video', 'original-series', 'films'):
            return self._get_vod_streams()


__plugin__ = OlympicChannel
