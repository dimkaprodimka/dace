#-plugin-sig:ZnaI3nxNl0qhpQwj57TlaJcuG/uXzPj22NHnpKXriWPJgSJy0at1pT+OzCNT1qkGEgi2LoX2VYIo+dnBtQ9h5KVsD+hfQAnlFqocb0Qfmh06mGZ2k+Fc/bYWPUwyg4ilLxymgNSTDmGKarm+zyvpM99hZVNZk/UIG48tI7XcpZwXdUtFzZ97wuk5zMbvbVm+pky1AfJNhDNzK14iDEuNGj73UKsfpkCVXSpc/n7bBbWtkuXVezXcR1X8QdaGC0Qt8IUj8RBgUd5dnIQ9c0GPgxJdmKTEpNiE8R5GMENWdtCtCv0cXYV4vK9i0yYuB9v5JVOTHLFDAV/YM2jtun6ltA==
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import urlparse, urlunparse
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HTTPStream, HLSStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json

log = logging.getLogger(__name__)


class RadioNet(Plugin):
    _url_re = re.compile(r"https?://(\w+)\.radio\.(net|at|de|dk|es|fr|it|pl|pt|se)")
    _stream_data_re = re.compile(r'\bstation\s*:\s*(\{.+\}),?\s*')

    _stream_schema = validate.Schema(
        validate.transform(_stream_data_re.search),
        validate.any(
            None,
            validate.all(
                validate.get(1),
                validate.transform(parse_json),
                {
                    'type': validate.text,
                    'streams': validate.all([{
                        'url': validate.url(),
                        'contentFormat': validate.text,
                    }])
                },
            )
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        streams = self.session.http.get(self.url, schema=self._stream_schema)
        if streams is None:
            return

        if streams['type'] != 'STATION':
            return

        stream_urls = set()
        for stream in streams['streams']:
            log.trace('{0!r}'.format(stream))
            url = stream['url']

            url_no_scheme = urlunparse(urlparse(url)._replace(scheme=''))
            if url_no_scheme in stream_urls:
                continue
            stream_urls.add(url_no_scheme)

            if stream['contentFormat'] in ('audio/mpeg', 'audio/aac'):
                yield 'live', HTTPStream(self.session, url, allow_redirects=True)
            elif stream['contentFormat'] == 'video/MP2T':
                streams = HLSStream.parse_variant_playlist(self.session, stream["url"])
                if not streams:
                    yield stream["quality"], HLSStream(self.session, stream["url"])
                else:
                    for s in streams.items():
                        yield s


__plugin__ = RadioNet
