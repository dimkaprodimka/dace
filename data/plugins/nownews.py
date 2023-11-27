#-plugin-sig:bEzZovlnHX1fAjrRPZa1Otyt3fojH0JJ7XnOs1xmAQOmNKSmLj8WYaXXVlGH6wEbUQ7cr9bRpwQabf6cG5bsMUctAcEn18VGu/nII/BDrIK5eJgAiYYiQhASibTGwJtD2UmS4wa7I3GIY5UyWZM3ckqHrRcTG9WcZfH8jt4KVLx5GF03iHuuF4eNbset8s+zotWzfAAlvXyHCMvE82Epr4uplzHsYnHw3yBvSYIncatz/cRTibZlGTw5GiYFfMbTUGTOTaP7zxQdRgeZ0pRzKgIhgjJT0Arz8EUBRf2aN2HqKKo5zBjMmAJ5Q7i+XVpLChDJVUbtyR2mhb2/kZwF3w==
import logging
import re
import json

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class NowNews(Plugin):
    _url_re = re.compile(r"https?://news.now.com/home/live")
    epg_re = re.compile(r'''epg.getEPG\("(\d+)"\);''')
    api_url = "https://hkt-mobile-api.nowtv.now.com/09/1/getLiveURL"
    backup_332_api = "https://d7lz7jwg8uwgn.cloudfront.net/apps_resource/news/live.json"
    backup_332_stream = "https://d3i3yn6xwv1jpw.cloudfront.net/live/now332/playlist.m3u8"

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        m = self.epg_re.search(res.text)
        channel_id = m and m.group(1)
        if channel_id:
            log.debug("Channel ID: {0}".format(channel_id))

            if channel_id == "332":
                # there is a special backup stream for channel 332
                bk_res = self.session.http.get(self.backup_332_api)
                bk_data = self.session.http.json(bk_res)
                if bk_data and bk_data["backup"]:
                    log.info("Using backup stream for channel 332")
                    return HLSStream.parse_variant_playlist(self.session, self.backup_332_stream)

            api_res = self.session.http.post(self.api_url,
                                             headers={"Content-Type": 'application/json'},
                                             data=json.dumps(dict(channelno=channel_id,
                                                                  mode="prod",
                                                                  audioCode="",
                                                                  format="HLS",
                                                                  callerReferenceNo="20140702122500")))
            data = self.session.http.json(api_res)
            for stream_url in data.get("asset", {}).get("hls", {}).get("adaptive", []):
                return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = NowNews
