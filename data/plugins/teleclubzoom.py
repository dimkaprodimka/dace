#-plugin-sig:ANRGwNVerIgekY0+LZhDWsf2YyHhJFIATAMmxZiuD0S6+T5gWtta6vN/6r5IiyNDBxVUS8Zas49joNF0EqbqUWTrpUofIElSC76FVw0HR4J2j0iR9OjDeH3BdpUYoaQEcqrEccz8bP5JoKFFHjHl3C8CUW5h4qXu/8sg9XMwtfTdp4QIeNu770BnHSdxOHM7paPKGHs9iBZvVO0mPo4dgFyl0//JwThETpK+4PLiAf6wtCPXglmXGt/h6t2c/Z5j+DrKVd1E1rOB401GGJMFUpZTXFDk5BCnAV5OWd5V+U/PHgJRX7/eQ+HtP4eoUNKxmG/t73mYLjLhDRzrqad6sg==
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import urlparse
from ACEStream.PluginsContainer.streamlink.exceptions import PluginError
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents, validate
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import itertags
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import update_scheme

log = logging.getLogger(__name__)


class TeleclubZoom(Plugin):

    _url_re = re.compile(r'https?://(?:www\.)?teleclubzoom\.ch')

    API_URL = 'https://{netloc}/webservice/http/rest/client/live/play/{id}'
    PLAYLIST_URL = 'https://{netloc}/{app}/ngrp:{name}_all/playlist.m3u8'

    _api_schema = validate.Schema(
        {
            'playStreamName': validate.text,
            'cdnHost': validate.text,
            'streamProperties': {
                validate.optional('server'): validate.text,
                validate.optional('name'): validate.text,
                'application': validate.text,
            }
        }
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        self.session.http.headers.update({'User-Agent': useragents.FIREFOX})

        iframe_url = None
        page = self.session.http.get(self.url)
        for a in itertags(page.text, 'a'):
            if a.attributes.get('class') == 'play-live':
                iframe_url = update_scheme(self.url, a.attributes['data-url'])
                break

        if not iframe_url:
            raise PluginError('Could not find iframe.')

        parsed = urlparse(iframe_url)
        path_list = parsed.path.split('/')
        if len(path_list) != 6:
            # only support a known iframe url style,
            # the video id might be on a different spot if the url changes
            raise PluginError('unsupported iframe URL: {0}'.format(iframe_url))

        res = self.session.http.get(
            self.API_URL.format(netloc=parsed.netloc, id=path_list[4]))

        data = self.session.http.json(res, schema=self._api_schema)
        log.trace('{0!r}'.format(data))

        url = self.PLAYLIST_URL.format(
            app=data['streamProperties']['application'],
            name=data['playStreamName'],
            netloc=data['cdnHost'],
        )
        return HLSStream.parse_variant_playlist(self.session, url)


__plugin__ = TeleclubZoom
