#-plugin-sig:QYgU3/G2yFJYBGr+dcDVnYwhCwq5hq6QLUbMWw1MfFhpmgnpmqidr8eUZfahT9l6zXnOt6uh5/ENPWQwwtf2fFF+TTRJzTPt9Aw0E9Uwb2t6UuovW214tbPCiIdOT8VmCGOuKmx0UEGs6Pklp3dv+4I+/qjcBAIFGZLehmc6ajF//Yc08U8o46CrwNQTVHBv+6xUH/4Ymcy/hxMi8SYBYnNZ9o8xZIVgMoAesiogatJLNVCXyFYVJP0st7gZ+ugXrEx1WcExr9786vFVeVloZ5+dZamWYN/rm/zNy5qMUIddjKIVzxZYi8EXLxNVJIfl4eMfQr0Zeu3PYwR0HCtuYw==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream, HTTPStream
from ACEStream.PluginsContainer.streamlink.utils.url import update_scheme


class Euronews(Plugin):
    _url_re = re.compile(r'(?P<scheme>https?)://(?P<subdomain>\w+)\.?euronews.com/(?P<path>live|.*)')
    _re_vod = re.compile(r'<meta\s+property="og:video"\s+content="(http.*?)"\s*/>')
    _live_api_url = "http://{0}.euronews.com/api/watchlive.json"
    _live_schema = validate.Schema({
        u"url": validate.url()
    })
    _stream_api_schema = validate.Schema({
        u'status': u'ok',
        u'primary': validate.url(),
        validate.optional(u'backup'): validate.url()
    })

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_vod_stream(self):
        """
        Find the VOD video url
        :return: video url
        """
        res = self.session.http.get(self.url)
        video_urls = self._re_vod.findall(res.text)
        if len(video_urls):
            return dict(vod=HTTPStream(self.session, video_urls[0]))

    def _get_live_streams(self, match):
        """
        Get the live stream in a particular language
        :param match:
        :return:
        """
        live_url = self._live_api_url.format(match.get("subdomain"))
        live_res = self.session.http.json(self.session.http.get(live_url), schema=self._live_schema)

        api_url = update_scheme("{0}:///".format(match.get("scheme")), live_res["url"])
        api_res = self.session.http.json(self.session.http.get(api_url), schema=self._stream_api_schema)

        return HLSStream.parse_variant_playlist(self.session, api_res["primary"])

    def _get_streams(self):
        """
        Find the streams for euronews
        :return:
        """
        match = self._url_re.match(self.url).groupdict()

        if match.get("path") == "live":
            return self._get_live_streams(match)
        else:
            return self._get_vod_stream()


__plugin__ = Euronews
