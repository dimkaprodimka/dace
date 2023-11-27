#-plugin-sig:aiAoqGZ/4E++9TS5CSqASf/xfld3sUtbrMYkn+ZSuij1M6AkEXp49W9Mjfqa3+5Uri8C7GJTN06LOcT0H/D708/1bcnwNNtwjWHgbQ/cILxezVuKhLI+1hvPJTalMAY9/R0jMA2CGSie1ldoMNVvWNo/eJaOTffPFH++nM2X11PtVWIS6geuxpH3ZIwi/iGvVbx8Fsm+Zf9nrf0ui1rokZtqPVjgJ56yepw8UdvONHz8F+xFbNdsMiqxFqS91rMw+tErxV9BzUSRRL9gSIXTnGstUSprweIB4jxRVBYkrG+nXg8iYho0ILn1i9XFYQHHe/hm5+diNElTS5Lhy7ZGJg==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class DRDK(Plugin):
    live_api_url = 'https://www.dr-massive.com/api/page'

    url_re = re.compile(r'''
        https?://(?:www\.)?dr\.dk/drtv
        (/kanal/[\w-]+)
    ''', re.VERBOSE)

    _live_data_schema = validate.Schema(
        {'item': {'customFields': {
            validate.optional('hlsURL'): validate.url(),
            validate.optional('hlsWithSubtitlesURL'): validate.url(),
        }}},
        validate.get('item'),
        validate.get('customFields'),
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_live(self, path):
        params = dict(
            ff='idp',
            path=path,
        )
        res = self.session.http.get(self.live_api_url, params=params)
        playlists = self.session.http.json(res, schema=self._live_data_schema)

        streams = {}
        for name, url in playlists.items():
            name_prefix = ''
            if name == 'hlsWithSubtitlesURL':
                name_prefix = 'subtitled_'

            streams.update(HLSStream.parse_variant_playlist(
                self.session,
                url,
                name_prefix=name_prefix,
            ))

        return streams

    def _get_streams(self):
        m = self.url_re.match(self.url)
        path = m and m.group(1)
        log.debug("Path={0}".format(path))

        return self._get_live(path)


__plugin__ = DRDK
