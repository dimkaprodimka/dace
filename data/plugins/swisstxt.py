#-plugin-sig:NkXTL8ptZqZyliDUYr7hJYz/LfDSBPUR8Q7czB/f/mCaTg4ahkReU3oC4t0K7tdfGFk173Ywo0wfOlUqSmTVcBEPvKKrNTozyKpjgUT3xsjH3DSC09hakkrcvU/ocTTk0Kly5VzIIvdJdRoHsOnlgVhZ8aEx+9NzCn1P8w3j9Lnzu8d8SpCmAu2zstdJWx8oQzCpCkSE0hTXnKLcJ5CK/5+V+Rw9N213F/vNwhzmN4zjrqCYNJEFPfskatPH0/Q9tS9cKfPubvT0PKqsy2eArTyI69HiBWjzU+PjgwWDZmvN17Iu5V26d6yUtwM84JhlDkvtbw/ZWrgTeP1lRdmaEw==
from __future__ import print_function

import re

from ACEStream.PluginsContainer.streamlink.compat import urlparse, parse_qsl, urlunparse
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class Swisstxt(Plugin):
    url_re = re.compile(r"""https?://(?:
        live\.(rsi)\.ch/|
        (?:www\.)?(srf)\.ch/sport/resultcenter
    )""", re.VERBOSE)
    api_url = "http://event.api.swisstxt.ch/v1/stream/{site}/byEventItemIdAndType/{id}/HLS"

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None and cls.get_event_id(url)

    @classmethod
    def get_event_id(cls, url):
        return dict(parse_qsl(urlparse(url).query.lower())).get("eventid")

    def get_stream_url(self, event_id):
        url_m = self.url_re.match(self.url)
        site = url_m.group(1) or url_m.group(2)
        api_url = self.api_url.format(id=event_id, site=site.upper())
        self.logger.debug("Calling API: {0}", api_url)

        stream_url = self.session.http.get(api_url).text.strip("\"'")

        parsed = urlparse(stream_url)
        query = dict(parse_qsl(parsed.query))
        return urlunparse(parsed._replace(query="")), query

    def _get_streams(self):
        stream_url, params = self.get_stream_url(self.get_event_id(self.url))
        return HLSStream.parse_variant_playlist(self.session,
                                                stream_url,
                                                params=params)


__plugin__ = Swisstxt
