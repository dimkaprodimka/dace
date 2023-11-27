#-plugin-sig:bCmtu/ykrak9aJP2dD0AKpaOSXHPwy1AEDktSHIqerjJZ5VMNDepUCBr7xtICvFIcSOFkDKrF1fTxLmkgzFP5lwScJfZxgUBa1/80y2NHpzihWuBHejb05biXVSINQU6vEoV41BHfDclDl0HF9nvVj0nvHZxS0Q5YXFj1OGO42ItwjxYD5482Pt62me/9KXP2vbD1sDcxQApuSO1Ko8/aHFG5dmUEAPTWTS5KGFqPD+1zbXFK8qrK9SfMttsnXuvkky97R31AdbgAG5aeB3iUOxK7fb//fNufwL+yzJO7p2yXckuCRyseDfin0dNlqpwpPgqfzJ883/VUNOZ5mvSOA==
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import html_unescape, urlparse
from ACEStream.PluginsContainer.streamlink.plugin import Plugin, PluginArguments, PluginArgument
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import DASHStream, HLSStream, HTTPStream
from ACEStream.PluginsContainer.streamlink.stream.ffmpegmux import MuxedStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json

log = logging.getLogger(__name__)


class Vimeo(Plugin):
    _url_re = re.compile(r"https?://(player\.vimeo\.com/video/\d+|(www\.)?vimeo\.com/.+)")
    _config_url_re = re.compile(r'(?:"config_url"|\bdata-config-url)\s*[:=]\s*(".+?")')
    _config_re = re.compile(r"var\s+config\s*=\s*({.+?})\s*;")
    _config_url_schema = validate.Schema(
        validate.transform(_config_url_re.search),
        validate.any(
            None,
            validate.Schema(
                validate.get(1),
                validate.transform(parse_json),
                validate.transform(html_unescape),
                validate.url(),
            ),
        ),
    )
    _config_schema = validate.Schema(
        validate.transform(parse_json),
        {
            "request": {
                "files": {
                    validate.optional("dash"): {"cdns": {validate.text: {"url": validate.url()}}},
                    validate.optional("hls"): {"cdns": {validate.text: {"url": validate.url()}}},
                    validate.optional("progressive"): validate.all(
                        [{"url": validate.url(), "quality": validate.text}]
                    ),
                },
                validate.optional("text_tracks"): validate.all(
                    [{"url": validate.text, "lang": validate.text}]
                ),
            }
        },
    )
    _player_schema = validate.Schema(
        validate.transform(_config_re.search),
        validate.any(None, validate.Schema(validate.get(1), _config_schema)),
    )

    arguments = PluginArguments(
        PluginArgument(
            "mux-subtitles",
            action="store_true",
            help="Automatically mux available subtitles in to the output stream.",
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url)

    def _get_streams(self):
        if "player.vimeo.com" in self.url:
            data = self.session.http.get(self.url, schema=self._player_schema)
        else:
            api_url = self.session.http.get(self.url, schema=self._config_url_schema)
            if not api_url:
                return
            data = self.session.http.get(api_url, schema=self._config_schema)

        videos = data["request"]["files"]
        streams = []

        for stream_type in ("hls", "dash"):
            if stream_type not in videos:
                continue
            for _, video_data in videos[stream_type]["cdns"].items():
                log.trace("{0!r}".format(video_data))
                url = video_data.get("url")
                if stream_type == "hls":
                    for stream in HLSStream.parse_variant_playlist(self.session, url).items():
                        streams.append(stream)
                elif stream_type == "dash":
                    p = urlparse(url)
                    if p.path.endswith("dash.mpd"):
                        # LIVE
                        url = self.session.http.get(url).json()["url"]
                    elif p.path.endswith("master.json"):
                        # VOD
                        url = url.replace("master.json", "master.mpd")
                    else:
                        log.error("Unsupported DASH path: {0}".format(p.path))
                        continue

                    for stream in DASHStream.parse_manifest(self.session, url).items():
                        streams.append(stream)

        for stream in videos.get("progressive", []):
            streams.append((stream["quality"], HTTPStream(self.session, stream["url"])))

        if self.get_option("mux_subtitles") and data["request"].get("text_tracks"):
            substreams = {
                s["lang"]: HTTPStream(self.session, "https://vimeo.com" + s["url"])
                for s in data["request"]["text_tracks"]
            }
            for quality, stream in streams:
                yield quality, MuxedStream(self.session, stream, subtitles=substreams)
        else:
            for stream in streams:
                yield stream


__plugin__ = Vimeo
