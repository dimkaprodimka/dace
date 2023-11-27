#-plugin-sig:DVOvPUzSYtVZ3KP/s57MSRLAhBt1BWSnD4SJEipVvmriiHGBcx1zS+bkI32KrlMCv4PMk1+4gfAj4hthgASX/xImKK0ausvCaSQiqAMnx1O42GIc49iBk3jTba3hxucQrLWZxovGJM+GHVzWQhZgxVo9yiKlYiKFFtwnxwzBkmjpa9e8uUrLgw6Bf4TS0ILCSAwOMXTqGIKwp+82hWzDqPbgOm9tyhvQZJqGFRD6bLPpCnUDfzlWucpEPvrrVJ4JL1ICniHSxgydOQ3MVCMg0nz0gW+xGiuVuydzDRJEtn0aQwTj9YHFRZoF1V6bhoSHlgwFCha1m25Bpa3RBOfIPg==
import re

from ACEStream.PluginsContainer.streamlink.compat import parse_qsl
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HTTPStream


class GoogleDocs(Plugin):
    url_re = re.compile(r"https?://(?:drive|docs).google.com/file/d/([^/]+)/?")
    api_url = "https://docs.google.com/get_video_info"

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        docid = self.url_re.match(self.url).group(1)
        self.logger.debug("Google Docs ID: {0}", docid)
        res = self.session.http.get(self.api_url, params=dict(docid=docid))
        data = dict(parse_qsl(res.text))

        if data["status"] == "ok":
            fmts = dict([s.split('/')[:2] for s in data["fmt_list"].split(",")])
            streams = [s.split('|') for s in data["fmt_stream_map"].split(",")]
            for qcode, url in streams:
                _, h = fmts[qcode].split("x")
                yield "{0}p".format(h), HTTPStream(self.session, url)
        else:
            self.logger.error("{0} (ID: {1})", data["reason"], docid)


__plugin__ = GoogleDocs
