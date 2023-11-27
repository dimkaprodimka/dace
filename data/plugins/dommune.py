#-plugin-sig:Yj+1ZlXHnx1/Y4vy6SM4zX6/OfzRnKiC9xPN5cRBiLWI/89yxm4O2dLu0HTxvkToFpbUbCSrlbeOxy2xzGNKJg+VugQWAydBj+xegmp5zWRQHMc63SaoYlwl/3C8pgn82FJSAO6LCjzActVifqEzyvHbmj3wLz1g49GsSAlDhS4nZr0dOM6Wr9t7F+O7B7iPaOLgmgafTYRYxa0b1Ja/SaDWOnA4n0YJVxEwWlVmcjTTHkx5i+0+X1/TT/K2ORbyGTU+Ssac2FBX1MzovOjQfTOaY3Yolmhb8DYgByNG1GdOknfCMI+CM3H81MwFo2bzrK7F5LxCTC8PoQobvpZ4NQ==
"""Plugin for DOMMUNE, simply extracts current live YouTube stream."""

import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate

DATA_URL = "http://www.dommune.com/freedommunezero2012/live/data/data.json"

_url_re = re.compile(r"http(s)?://(\w+\.)?dommune.com")
_data_schema = validate.Schema({
    "channel": validate.text,
    "channel2": validate.text
})


class Dommune(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        res = self.session.http.get(DATA_URL)
        data = self.session.http.json(res, schema=_data_schema)
        video_id = data["channel"] or data["channel2"]
        if not video_id:
            return

        url = "http://youtu.be/{0}".format(video_id)
        return self.session.streams(url)


__plugin__ = Dommune
