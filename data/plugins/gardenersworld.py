#-plugin-sig:bQNXBlJM3hnzfFhdILTU0VTby0eezV4GNx8F52+NGNHKNAEpYm1+cRfV1836UfyLX+IOBTeNFVhqN/VjVm5hYtuxvWBimxEjFm1cNGOs0oFq38wb7iiY+5YPhlXGGRCGO//5bvqHAYet2h9A0pg9MsXk0AKUG679tYrjO2i5elhOwWyVVruxuCry6SWzhSWp4ZL2tpqp3ZvGe9UKFlqYf1RRTgv4bTw2dhaDomg/263R5937WwinhnXOacikfcmT4mKGPYL/f3zj8Xz39eddKgN/hs8iHxkGIBnuY36PzE/OSLV+5i65Pe04t6PH9rQwMeQmI5LrODCvGUMm1hh7Rw==
from __future__ import print_function

import re

from ACEStream.PluginsContainer.streamlink import NoPluginError
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import itertags
from ACEStream.PluginsContainer.streamlink.utils import update_scheme


class GardenersWorld(Plugin):
    url_re = re.compile(r"https?://(?:www\.)?gardenersworld\.com/")

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        page = self.session.http.get(self.url)
        for iframe in itertags(page.text, u"iframe"):
            url = iframe.attributes["src"]
            self.logger.debug("Handing off of {0}".format(url))
            try:
                return self.session.streams(update_scheme(self.url, url))
            except NoPluginError:
                self.logger.error("Handing off of {0} failed".format(url))
                return None


__plugin__ = GardenersWorld
