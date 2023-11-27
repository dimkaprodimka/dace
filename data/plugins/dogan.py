# -*- coding: utf-8 -*-
#-plugin-sig:m92eGsw7iqFx3P+Z5iyyn/uh/m9rc3uekOR0Z9MQqS13KXtuWL2i0Hai1HLUSY7PtlWi3SStD9dS+WKWuSzh3O1AIvtlraTqDP+rPUScwqwaLN2GiFJb4xNIzHwPMMmYNHH8+O+nI6BcOMXSVpJskZc3nKFSEPRYrJOZHxbRkq/Z3uz909JO/oiSIYqEoo0LsuEPBtHUNNofk/8W8TZg28bdK6dplgFtZ2FFZTzf5eeOoz6HiZ2f7LXePHXsmFxRim6RCMlsY8VWU5dj/bbJm1ZA3kNio204AyM+TWU/NMiB8ACY4LkBO3RuZFmWnXFBiSFrVN+O1qv9Z7Qj9zkNFQ==
from __future__ import print_function

import re

from ACEStream.PluginsContainer.streamlink.compat import urljoin
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream


class Dogan(Plugin):
    """
    Support for the live streams from Doğan Media Group channels
    """
    url_re = re.compile(r"""
        https?://(?:www.)?
        (?:teve2.com.tr/(?:canli-yayin|filmler/.*|programlar/.*)|
           kanald.com.tr/.*|
           cnnturk.com/canli-yayin|
           dreamtv.com.tr/canli-yayin|
           dreamturk.com.tr/canli)
    """, re.VERBOSE)
    playerctrl_re = re.compile(r'''<div[^>]*?ng-controller=(?P<quote>["'])(?:Live)?PlayerCtrl(?P=quote).*?>''', re.DOTALL)
    data_id_re = re.compile(r'''data-id=(?P<quote>["'])(?P<id>\w+)(?P=quote)''')
    content_id_re = re.compile(r'"content(?:I|i)d", "(\w+)"')
    item_id_re = re.compile(r"_itemId\s+=\s+'(\w+)';")
    content_api = "/actions/content/media/{id}"
    new_content_api = "/action/media/{id}"
    content_api_schema = validate.Schema({
        "Id": validate.text,
        "Media": {
            "Link": {
                "DefaultServiceUrl": validate.url(),
                validate.optional("ServiceUrl"): validate.any(validate.url(), ""),
                "SecurePath": validate.text,
            }
        }
    })

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_content_id(self):
        res = self.session.http.get(self.url)
        # find the contentId
        content_id_m = self.content_id_re.search(res.text)
        if content_id_m:
            self.logger.debug("Found contentId by contentId regex")
            return content_id_m.group(1)

        # find the PlayerCtrl div
        player_ctrl_m = self.playerctrl_re.search(res.text)
        if player_ctrl_m:
            # extract the content id from the player control data
            player_ctrl_div = player_ctrl_m.group(0)
            content_id_m = self.data_id_re.search(player_ctrl_div)
            if content_id_m:
                self.logger.debug("Found contentId by player data-id regex")
                return content_id_m.group("id")

        # find the itemId var
        item_id_m = self.item_id_re.search(res.text)
        if item_id_m:
            self.logger.debug("Found contentId by itemId regex")
            return item_id_m.group(1)

    def _get_hls_url(self, content_id):
        # make the api url relative to the current domain
        if "cnnturk" in self.url or "teve2.com.tr" in self.url:
            self.logger.debug("Using new content API url")
            api_url = urljoin(self.url, self.new_content_api.format(id=content_id))
        else:
            api_url = urljoin(self.url, self.content_api.format(id=content_id))

        apires = self.session.http.get(api_url)

        stream_data = self.session.http.json(apires, schema=self.content_api_schema)
        d = stream_data["Media"]["Link"]
        return urljoin((d["ServiceUrl"] or d["DefaultServiceUrl"]), d["SecurePath"])

    def _get_streams(self):
        content_id = self._get_content_id()
        if content_id:
            self.logger.debug(u"Loading content: {}", content_id)
            hls_url = self._get_hls_url(content_id)
            return HLSStream.parse_variant_playlist(self.session, hls_url)
        else:
            self.logger.error(u"Could not find the contentId for this stream")


__plugin__ = Dogan
