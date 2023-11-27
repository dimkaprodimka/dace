#-plugin-sig:if0K2e5BfUSEhwLtU1XgNymf2n4g9q95ULP6Opm/lwIn7Smc5HzyiPkQaGh5LwI9BEOwKQmNpiZKwClF+xDZTzF++GpjBjCAF6KmRngCN4SCSmcoxq55VCMIJXvDHmB/3FZb7mb8erwFQ33kJypyKrIc2jgyXhx5YZXpc7rCG3GAUrvLVzGiuHRzYbQgATbX9FsP6n+x2tlxQsuOBVdYg3T02OGD+wmk2eEIlHltV93isdeXuKrWNYNEs30WB9Agmtgd1XOgIeS65bYKXZsAup4aTNy6VUa86kUHSGKYIT3x/sCvLG4SbVuysVBSrWEHxryiXr4llEBeJxRtD080vQ==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HTTPStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json, update_scheme


class Streamable(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?streamable\.com/(.+)")
    meta_re = re.compile(r'''var\s*videoObject\s*=\s*({.*});''')
    config_schema = validate.Schema(
        validate.transform(meta_re.search),
        validate.any(None,
                     validate.all(
                         validate.get(1),
                         validate.transform(parse_json),
                         {
                             "files": {validate.text: {"url": validate.url(),
                                                       "width": int,
                                                       "height": int,
                                                       "bitrate": int}}
                         })
                     )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        data = self.session.http.get(self.url, schema=self.config_schema)

        for info in data["files"].values():
            stream_url = update_scheme(self.url, info["url"])
            # pick the smaller of the two dimensions, for landscape v. portrait videos
            res = min(info["width"], info["height"])
            yield "{0}p".format(res), HTTPStream(self.session, stream_url)


__plugin__ = Streamable
