#-plugin-sig:Tvg5oKB2ke4/p7idJ/toFktl5ksGzZxdu5nilvMRxPfhdCIgb91K0y1tr2BnfbA3oAav+Xnp2/jtDQ6GeSFVrOzcSrjIyyaYlreboW/7h6RYy8T8xyGkbD0Gp3nBy70LXhdCiZp9rYf/wFioQh2aMBUZP9Wa6+EPuoBONPpcH6uo8zC9vY90Q9mF8iUA2LqW+n69nIFpTTN7JIRNyVGcuIVkkJUBqsixhmsQW98j1/QMX/vxLHUl/HHUR8A2yFqcEq2LoZrY5ZK5yGaelW9a3SP/6oiowaK1dL0kJrSZmG/zT3WRIjYQ8tQ91jdWHFaMC3pe/kVuFXnHCm7yq+y4xQ==
import logging
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin, PluginArgument, PluginArguments
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

log = logging.getLogger(__name__)


class ClubbingTV(Plugin):
    _login_url = "https://www.clubbingtv.com/user/login"

    _url_re = re.compile(r"https://(www\.)?clubbingtv\.com/")
    _live_re = re.compile(
        r'playerInstance\.setup\({\s*"file"\s*:\s*"(?P<stream_url>.+?)"',
        re.DOTALL,
    )
    _vod_re = re.compile(r'<iframe src="(?P<stream_url>.+?)"')

    arguments = PluginArguments(
        PluginArgument(
            "username",
            required=True,
            requires=["password"],
            help="The username used to register with Clubbing TV.",
        ),
        PluginArgument(
            "password",
            required=True,
            sensitive=True,
            help="A Clubbing TV account password to use with --clubbingtv-username.",
        ),
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def login(self):
        username = self.get_option("username")
        password = self.get_option("password")
        res = self.session.http.post(
            self._login_url,
            data={"val[login]": username, "val[password]": password},
        )

        if "Invalid Email/User Name" in res.text:
            log.error(
                "Failed to login to Clubbing TV, incorrect email/password combination"
            )
            return False

        log.info("Successfully logged in")
        return True

    def _get_live_streams(self, content):
        match = self._live_re.search(content)
        if not match:
            return
        stream_url = match.group("stream_url")

        for stream in HLSStream.parse_variant_playlist(
            self.session, stream_url
        ).items():
            yield stream

    def _get_vod_streams(self, content):
        match = self._vod_re.search(content)
        if not match:
            return

        stream_url = match.group("stream_url")
        log.info(
            "Fetching external stream from URL {0}".format(stream_url)
        )
        return self.session.streams(stream_url)

    def _get_streams(self):
        if not self.login():
            return

        self.session.http.headers.update({"Referer": self.url})

        res = self.session.http.get(self.url)

        if "clubbingtv.com/live" in self.url:
            log.debug("Live stream detected")
            return self._get_live_streams(res.text)

        log.debug("VOD stream detected")
        return self._get_vod_streams(res.text)


__plugin__ = ClubbingTV
