#-plugin-sig:hizR470kGJtUBS9gOP8qUFpQG1syKWkaZj581DckllefEUOzrKqvPC4dye6zYczLvXIS0hfqUKHpQ2oCfN9w88wQXmxRZOMLDOYwwRK4XcYX47HbPxAlFwmP4bwaEhVSU94R5u41ZwWRymynIYQvLUePG9e5O4gO8nmr5JKqgpYaqXl+Ml6NPo4+qUl5Lir58iQwhIiMtM/+RjXGAijPfcEqZg4S+MH96H0y5wAsNxNFcIEELSMkfl69ByyD4rhn7WVqZ1lny8mWpCLLQ4wkXWuPQErh2mz1Y4fs8eU/pko/1bPTc+BneX1EnwRW1dQ/Ec7dWInVZqdXuxfgO9OBEw==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class ZengaTV(Plugin):
    """Streamlink Plugin for livestreams on zengatv.com"""

    _url_re = re.compile(r"https?://(www\.)?zengatv\.com/\w+")
    _id_re = re.compile(r"""id=(?P<q>["'])dvrid(?P=q)\svalue=(?P=q)(?P<id>[^"']+)(?P=q)""")
    _id_2_re = re.compile(r"""LivePlayer\(.+["'](?P<id>D\d+)["']""")

    api_url = "http://www.zengatv.com/changeResulation/"

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        headers = {
            "User-Agent": useragents.FIREFOX,
            "Referer": self.url,
        }

        res = self.session.http.get(self.url, headers=headers)
        for id_re in (self._id_re, self._id_2_re):
            m = id_re.search(res.text)
            if not m:
                continue
            break

        if not m:
            self.logger.error("No video id found")
            return

        dvr_id = m.group("id")
        self.logger.debug("Found video id: {0}".format(dvr_id))
        data = {"feed": "hd", "dvrId": dvr_id}
        res = self.session.http.post(self.api_url, headers=headers, data=data)
        if res.status_code == 200:
            for s in HLSStream.parse_variant_playlist(self.session, res.text, headers=headers).items():
                yield s


__plugin__ = ZengaTV
