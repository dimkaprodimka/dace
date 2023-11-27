#-plugin-sig:EZa+MO9JrSLP7ZFQfFsVeFpQh2HDXLEMVXCp3j32pONpWamaJmsRoxrESaSSGtbYFgqiwMeH4dJXxcWmBz2lqTnMZTjYhMcxMlbvaO6JLk3rKwHQUVagOYyYeH34VZMkoQrLvasmcmY6CNaZEzkJo08MgLVjr0FFNrM7P2hbEbGhjC0YAQSgFZFSH5axwmVQhM1LUKEGm4TxxXKu9vfE/0b9pHFhOxFT0oW6knIsqQBPFrIZC6nQoMxR3Rg9Z2icAQomUnzEmj3c5V6sk1ig9Wg9GZ7gehdiEIHgXP/vGPFEPcgVeQL+kSfkl9yjHGkdOPJtZ/lXd5UJ+06QBgm0DQ==
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import html_unescape
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import itertags

log = logging.getLogger(__name__)


class Willax(Plugin):
    _url_re = re.compile(r'https?://(?:www\.)?willax\.tv/en-vivo')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        self.session.http.headers.update({'User-Agent': useragents.FIREFOX})
        res = self.session.http.get(self.url)
        for iframe in itertags(res.text, 'iframe'):
            return self.session.streams(html_unescape(iframe.attributes.get('src')))


__plugin__ = Willax
