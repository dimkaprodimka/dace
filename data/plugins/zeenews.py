#-plugin-sig:THNe1U9tK6GkyUTSYSK1zbkwCp/rDTbu0o1wbrwsDqxI4nrDAcEwX/l5RuBKDU0Qby0icUM1ZKUrspKIZ5h4VuysxBLwPGLb0OZ4SZjGqQGv8xqYvs2V+sDg9vHTO7Rf7t4cB5mfNWlwEQshkmUg7IhyUihYINKyyD6GWKG7tzrtAYMvpUZ8Od/04WSYQKOC4Bx1Fv0ZXF/Gq+z86D6DCMtdZzdIfV9ycRKYVokDXwHDGrw0j5sn/8wVE5zW/aW9F1OEK00EwKziicUaPVNpkIaHwHtm6CHEawSfp7mRz0hNuu1pwl44RJjFY58BAurrZiKSRahIrZPEzzeD0rb8Cw==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class ZeeNews(Plugin):
    _url_re = re.compile(r'https?://zeenews\.india\.com/live-tv')

    HLS_URL = 'https://z5ams.akamaized.net/zeenews/index.m3u8{0}'
    TOKEN_URL = 'https://useraction.zee5.com/token/live.php'

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def get_title(self):
        return 'Zee News'

    def _get_streams(self):
        res = self.session.http.get(self.TOKEN_URL)
        token = self.session.http.json(res)['video_token']
        log.debug('video_token: {0}'.format(token))
        for s in HLSStream.parse_variant_playlist(self.session, self.HLS_URL.format(token)).items():
            yield s


__plugin__ = ZeeNews
