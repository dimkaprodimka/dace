#-plugin-sig:FkILruPDtqEjEkuGrvIwjqhRn7d0Xtj3tuqVoU11/sJ48AWdzxExNA9CDIydLPKZ0K1mtcxIEanCr8Nesjx/6UqOKuP46hP2Iu1wAIaVcc++j1LwsMOBQF8fSCEXFxXw3ND5mSA07RNugTjODW5moDcnVanvWccr35j/yfrp9wLu6FcpT0/srDPgoepIbhE7VhWfZXu78C2Ox30jBs27qkqyRQGmHkc5xFIu7C/b+VbGZTEVFoMwD9B4GAxO4QZOPQmjrox1Y/yKtYfI33Ymf4ks96O4+OwQp4TF91Gkea1ZiuJjV1zpk2KTIG2SsHFd4NevHRb7fGpROLALo16TLg==
from __future__ import print_function

import re
import json

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.stream import RTMPStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json


class Picarto(Plugin):
    CHANNEL_API_URL = "https://api.picarto.tv/v1/channel/name/{channel}"
    VIDEO_API_URL = "https://picarto.tv/process/channel"
    RTMP_URL = "rtmp://{server}:1935/play/"
    RTMP_PLAYPATH = "golive+{channel}?token={token}"
    HLS_URL = "https://{server}/hls/{channel}/index.m3u8?token={token}"

    # Regex for all usable URLs
    _url_re = re.compile(r"""
        https?://(?:\w+\.)?picarto\.tv/(?:videopopout/)?([^&?/]+)
    """, re.VERBOSE)

    # Regex for VOD extraction
    _vod_re = re.compile(r'''(?<=#vod-player", )(\{.*?\})''')

    data_schema = validate.Schema(
        validate.transform(_vod_re.search),
        validate.any(
            None,
            validate.all(
                validate.get(0),
                validate.transform(parse_json),
                {
                    "vod": validate.url(),
                }
            )
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _create_hls_stream(self, server, channel, token):
        streams = HLSStream.parse_variant_playlist(self.session,
                                                   self.HLS_URL.format(
                                                       server=server,
                                                       channel=channel,
                                                       token=token),
                                                   verify=False)
        if len(streams) > 1:
            self.logger.debug("Multiple HLS streams found")
            return streams
        elif len(streams) == 0:
            self.logger.warning("No HLS streams found when expected")
            return {}
        else:
            # one HLS streams, rename it to live
            return {"live": list(streams.values())[0]}

    def _create_flash_stream(self, server, channel, token):
        params = {
            "rtmp": self.RTMP_URL.format(server=server),
            "playpath": self.RTMP_PLAYPATH.format(token=token, channel=channel)
        }
        return RTMPStream(self.session, params=params)

    def _get_vod_stream(self, page):
        data = self.data_schema.validate(page.text)

        if data:
            return HLSStream.parse_variant_playlist(self.session, data["vod"])

    def _get_streams(self):
        url_channel_name = self._url_re.match(self.url).group(1)

        # Handle VODs first, since their "channel name" is different
        if url_channel_name.endswith((".flv", ".mkv")):
            self.logger.debug("Possible VOD stream...")
            page = self.session.http.get(self.url)
            vod_streams = self._get_vod_stream(page)
            if vod_streams:
                for s in vod_streams.items():
                    yield s
                return
            else:
                self.logger.warning("Probably a VOD stream but no VOD found?")

        ci = self.session.http.get(self.CHANNEL_API_URL.format(channel=url_channel_name), raise_for_status=False)

        if ci.status_code == 404:
            self.logger.error("The channel {0} does not exist".format(url_channel_name))
            return

        channel_api_json = json.loads(ci.text)

        if not channel_api_json["online"]:
            self.logger.error("The channel {0} is currently offline".format(url_channel_name))
            return

        server = None
        token = "public"
        channel = channel_api_json["name"]

        # Extract preferred edge server and available techs from the undocumented channel API
        channel_server_res = self.session.http.post(self.VIDEO_API_URL, data={"loadbalancinginfo": channel})
        info_json = json.loads(channel_server_res.text)
        pref = info_json["preferedEdge"]
        for i in info_json["edges"]:
            if i["id"] == pref:
                server = i["ep"]
                break
        self.logger.debug("Using load balancing server {0} : {1} for channel {2}",
                          pref,
                          server,
                          channel)

        for i in info_json["techs"]:
            if i["label"] == "HLS":
                for s in self._create_hls_stream(server, channel, token).items():
                    yield s
            elif i["label"] == "RTMP Flash":
                stream = self._create_flash_stream(server, channel, token)
                yield "live", stream


__plugin__ = Picarto
