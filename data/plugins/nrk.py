#-plugin-sig:UdCJHCc5krDW8hKLoEqyRSmHDtaipVkiP+Fxbz45yp+264fIHTy4OFcw2dK0KAtk4OyxQ/OXpw63RWkfZSSfL0vx6s7+SBlGsWXAhQ+qoQjCo+NqOOCRbS4G29v4uQLE5+kNswotj47HMKkQI7SN7Z15vxunfOS47ZTl5Idgb9Ri99PwYyGKr3UGO+UboqSarVrMoTOOSiZtFKZUooPBVbJz1XASNWystIukJVTqs+FzugN8lIXChEh0HzV+vYJm6iv0Hh15PS9awCbtf1QNRMBflt2v8WnK5dkRqytpCsdd69xvE1eHYImS9cjGWJctGo/xTv7+3MDIRLTUCC9bIw==
import re

from ACEStream.PluginsContainer.streamlink.compat import urljoin
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream

COOKIE_PARAMS = (
    "devicetype=desktop&"
    "preferred-player-odm=hlslink&"
    "preferred-player-live=hlslink"
)

_id_re = re.compile(r"/(?:program|direkte|serie/[^/]+)/([^/]+)")
_url_re = re.compile(r"https?://(tv|radio).nrk.no/")
_api_baseurl_re = re.compile(r'''apiBaseUrl:\s*["'](?P<baseurl>[^"']+)["']''')

_schema = validate.Schema(
    validate.transform(_api_baseurl_re.search),
    validate.any(
        None,
        validate.all(
            validate.get("baseurl"),
            validate.url(
                scheme="http"
            )
        )
    )
)

_mediaelement_schema = validate.Schema({
    "mediaUrl": validate.url(
        scheme="http",
        path=validate.endswith(".m3u8")
    )
})


class NRK(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        # Get the stream type from the url (tv/radio).
        stream_type = _url_re.match(self.url).group(1).upper()
        cookie = {
            "NRK_PLAYER_SETTINGS_{0}".format(stream_type): COOKIE_PARAMS
        }

        # Construct API URL for this program.
        baseurl = self.session.http.get(self.url, cookies=cookie, schema=_schema)
        program_id = _id_re.search(self.url).group(1)

        # Extract media URL.
        json_url = urljoin(baseurl, "mediaelement/{0}".format(program_id))
        res = self.session.http.get(json_url, cookies=cookie)
        media_element = self.session.http.json(res, schema=_mediaelement_schema)
        media_url = media_element["mediaUrl"]

        return HLSStream.parse_variant_playlist(self.session, media_url)


__plugin__ = NRK
