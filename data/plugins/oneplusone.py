#-plugin-sig:bXWkf32LGCjnpaaAGl+ivGATNJyS1/kDu4au6FM4j0c1mG0B3v/v1249XG697l8JH/zq5102H5bx1BH6+9kQhpw9qqH324IUYclm6Smn/MJlUe9OxMEMEhK6qn/8mHGt7MUKIR2STsJgd8ZWFbYHoVRBpyINlW9k6GY9hd6fYpdiS2amPQkSO2iM04NPH/Ot/uXSnHlIlewWeVxhgB7mWeU70CZrRDGMj+CO+O6bc9D1/ZC7V/Xp0iYaquBWVcMs5TZltEP9GKDLLQG1lXR1uAASDvcIr7FugXGn8I4JgoFNy+LgiYC9Gg6JAuBRMgET3RWPlCJ/AG3L4UOzOzUifA==
import logging
import re

from base64 import b64decode
from ACEStream.PluginsContainer.streamlink.compat import urlparse
from ACEStream.PluginsContainer.streamlink.exceptions import PluginError
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

log = logging.getLogger(__name__)


class Online_Parser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'iframe':
            attrs = dict(attrs)
            if 'name' in attrs and attrs['name'] == 'twttrHubFrameSecure':
                self.iframe_url = attrs['src']


class Iframe_Parser(HTMLParser):
    js = False

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            attrs = dict(attrs)
            if 'type' in attrs and attrs['type'] == 'text/javascript':
                self.js = True

    def handle_data(self, data):
        if self.js and data.startswith('window.onload'):
            self.data = data


class OnePlusOne(Plugin):
    url_re = re.compile(r'https://1plus1\.video/tvguide/.*/online')
    data_re = re.compile(r"ovva-player\",\"([^\"]*)\"\)")
    ovva_data_schema = validate.Schema({
        "balancer": validate.url()
    }, validate.get("balancer"))
    ovva_redirect_schema = validate.Schema(validate.all(
        validate.transform(lambda x: x.split("=")),
        ['302', validate.url()],
        validate.get(1)
    ))

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def find_iframe(self, res):
        parser = Online_Parser()
        parser.feed(res.text)
        url = parser.iframe_url
        if url.startswith("//"):
            p = urlparse(self.url)
            return "{0}:{1}".format(p.scheme, url)
        else:
            return url

    def get_data(self, res):
        parser = Iframe_Parser()
        parser.feed(res.text)
        if hasattr(parser, "data"):
            m = self.data_re.search(parser.data)
            if m:
                data = m.group(1)
                return data

    def _get_streams(self):
        self.session.http.headers.update({"User-Agent": useragents.FIREFOX})
        res = self.session.http.get(self.url)
        iframe_url = self.find_iframe(res)
        if iframe_url:
            log.debug("Found iframe: {0}".format(iframe_url))
            res = self.session.http.get(
                iframe_url,
                headers={"Referer": self.url})
            data = self.get_data(res)
            if data:
                try:
                    ovva_url = parse_json(
                        b64decode(data).decode(),
                        schema=self.ovva_data_schema)
                    log.debug("Found ovva: {0}".format(ovva_url))

                    stream_url = self.session.http.get(
                        ovva_url,
                        schema=self.ovva_redirect_schema,
                        headers={"Referer": iframe_url})
                    log.debug("Found stream: {0}".format(stream_url))

                except PluginError as e:
                    log.error("Could not find stream URL: {0}".format(e))
                else:
                    return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = OnePlusOne
