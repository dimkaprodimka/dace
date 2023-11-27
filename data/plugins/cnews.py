#-plugin-sig:lN5ayIbLNKOamDmEThhdOHzLd4feeOF06yc6+fLe88TrMHcBSu6qykJupllqlv3fT25rdLK9c3XlFvzjEvZwM5i/txV2BooWJm7AyIHFSVQNcWr33VUZIvjlNZOQWC6tdacp5nS8hNNUqFmGWFJBj2+0hK+4XyL9kHaU6DkhP4y9Cuq2E4JAOnclDRNPFiAwnAcqf2BqJT8EMsC2CHbwd9OasQ5AM/1nOlx6rTHx9QJ+9d33WtrYi1auE3n6Bf2zKb6ZQca3hLSGEhkQ8+VwrTnpNoDHBO2+l45oNgFZYap4ACYBlZ4RqoZhZu/l2TSZIs1pHcN7WqgHa0b50uJxMg==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import useragents


class CNEWS(Plugin):
    _url_re = re.compile(r'https?://www.cnews.fr/[^ ]+')
    _embed_video_url_re = re.compile(r'class="dm-video-embed_video" src="(?P<dm_url>.*)"')
    _embed_live_url_re = re.compile(r'class="wrapper-live-player main-live-player"><iframe src="(?P<dm_url>.*)"')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        # Retrieve URL page and search for Dailymotion URL
        res = self.session.http.get(self.url, headers={'User-Agent': useragents.CHROME})
        match = self._embed_live_url_re.search(res.text) or self._embed_video_url_re.search(res.text)
        if match is not None:
            return self.session.streams(match.group('dm_url'))


__plugin__ = CNEWS
