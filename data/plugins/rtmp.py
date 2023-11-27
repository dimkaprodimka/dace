#-plugin-sig:Jc4tQCqC/j35O50enoe9lHVKH6vS4VWZqtRftUQUc9XVXPNde3rQnyFU4ArTk/0+qm1bAOAq/fMIlMTn/O3RcdxJSYVBOpcpmTeUMdTeGJLoKkZsPhWkBq2jnta+yKMBavogEQJvvDUczFEAltANKHV+rk3pO1JBforRFqYkk4VK/SyMJwV2fXx6P336mFq+ds6WxOmB5UqoeGmcFHfWYSt141H6kTxaMkc3gC/+kYLTqVVSstC8QjQdES6qljxxgxJMXXIcF0Po3MJJFU/6FY9nqmfJxWUMvzkdSJBOvc2fh7aAaxr9GGdi58Pv+OmBW5IOOs0xFMhc8lQzI84jPg==
import re

from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.plugin import parse_url_params
from ACEStream.PluginsContainer.streamlink.stream import RTMPStream


class RTMPPlugin(Plugin):
    _url_re = re.compile(r"rtmp(?:e|s|t|te)?://.+")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        url, params = parse_url_params(self.url)
        params["rtmp"] = url

        for boolkey in ("live", "realtime", "quiet", "verbose", "debug"):
            if boolkey in params:
                params[boolkey] = bool(params[boolkey])

        self.logger.debug("params={0}", params)
        return {"live": RTMPStream(self.session, params)}


__plugin__ = RTMPPlugin
