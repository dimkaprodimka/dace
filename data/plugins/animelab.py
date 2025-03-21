#-plugin-sig:kDrAqY1tsVqcGGQWkQbTUCXGg6NzsMieFGQ0YCjv85OdEvr8Bp+yNqEwJ+JoEr4U/32Qw6TFS1NRk+dAN9/4hf2of5OQi9BphIiZg8vQ0khZV6IphqMgUZkIBRHZJAisEBh7Izq0RwlrwpAnJRzlorb+y87Y1haeVlF0UdRJH8npc0oW/WeDGFrMYZlVuJtub02HBVGBfEgftcGFG1Bs8L/T7hyjQvGRYi1w4A0pX/OWQsagAlUkfdik2Kkr5khWEibuzz2yKulDHt7nbDM95DIPo041OWHd5IosL4zJRdmaHnH+NvFUC0r+f7DcIbGdjO/v6yzhCIiFLx8vjIaoyw==
from __future__ import print_function
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin, PluginArguments, PluginArgument
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HTTPStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json


class AnimeLab(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?animelab\.com/player/")
    login_url = "https://www.animelab.com/login"
    video_collection_re = re.compile(r"VideoCollection\((\[.*?\])\);")
    playlist_position_re = re.compile(r"playlistPosition\s*=\s*(\d+);")
    video_collection_schema = validate.Schema(
        validate.union({
            "position": validate.all(
                validate.transform(playlist_position_re.search),
                validate.any(
                    None,
                    validate.all(validate.get(1), validate.transform(int))
                )
            ),
            "playlist": validate.all(
                validate.transform(video_collection_re.search),
                validate.any(
                    None,
                    validate.all(
                        validate.get(1),
                        validate.transform(parse_json)
                    )
                )
            )
        })
    )
    arguments = PluginArguments(
        PluginArgument(
            "email",
            requires=["password"],
            metavar="EMAIL",
            help="The email address used to register with animelab.com."
        ),
        PluginArgument(
            "password",
            sensitive=True,
            metavar="PASSWORD",
            help="A animelab.com account password to use with --animelab-email."
        )
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def login(self, email, password):
        self.logger.debug("Attempting to log in as {0}", email)
        res = self.session.http.post(
            self.login_url,
            data=dict(email=email, password=password),
            allow_redirects=False,
            raise_for_status=False
        )
        loc = res.headers.get("Location", "")
        if "geoblocked" in loc.lower():
            self.logger.error("AnimeLab is not available in your territory")
        elif res.status_code >= 400:
            self.logger.error("Failed to login to AnimeLab, check your email/password combination")
        else:
            return True

        return False

    def _get_streams(self):
        email, password = self.get_option("email"), self.get_option("password")
        if not email or not password:
            self.logger.error("AnimeLab requires authentication, use --animelab-email "
                              "and --animelab-password to set your email/password combination")
            return

        if self.login(email, password):
            self.logger.info("Successfully logged in as {0}", email)
            video_collection = self.session.http.get(self.url, schema=self.video_collection_schema)
            if video_collection["playlist"] is None or video_collection["position"] is None:
                return

            data = video_collection["playlist"][video_collection["position"]]

            self.logger.debug("Found {0} version {1} hard-subs",
                              data["language"]["name"],
                              "with" if data["hardSubbed"] else "without")

            for video in data["videoInstances"]:
                if video["httpUrl"]:
                    q = video["videoQuality"]["description"]
                    s = HTTPStream(self.session, video["httpUrl"])
                    yield q, s


__plugin__ = AnimeLab
