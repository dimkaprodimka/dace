#-plugin-sig:UPR2xUl7GWgig/81U78IBfqEl6BlWF/TfP+U3p1BqVNisetQt2K7MZ2dKHhQF0e5xyjgfSjLeqw2ApdT+XFAFRQjSSSw4dDCCSiWDNwgFwlIHmvQB7TycQDB6voL8fVCSl0RQT4CCrjCptj64nxq++WZYV4QIyzPDdlahUIl/MDU19ChlrwDwCfiYuFTlc0Hb9uIIUbYR1c3d5jMsppsiR/urFY6/mcl0FK0xTZZj/e1gwqtUp/n1eYuTsNpEu4TkiwzfLR0iG9OSnsVPaz5L6rN1akITdadyd9l46LLg88AaUvTUqA4sAR6j7kA8adK8d13DLbjzE85tCCYv+69Kg==
import re

from functools import partial

from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.plugin.api.utils import parse_json

__all__ = ["parse_playlist"]

_playlist_re = re.compile(r"\(?\{.*playlist: (\[.*\]),.*?\}\)?;", re.DOTALL)
_js_to_json = partial(re.compile(r"(\w+):\s").sub, r'"\1":')

_playlist_schema = validate.Schema(
    validate.transform(_playlist_re.search),
    validate.any(
        None,
        validate.all(
            validate.get(1),
            validate.transform(_js_to_json),
            validate.transform(parse_json),
            [{
                "sources": [{
                    "file": validate.text,
                    validate.optional("label"): validate.text
                }]
            }]
        )
    )
)


def parse_playlist(res):
    """Attempts to parse a JWPlayer playlist in a HTTP response body."""
    return _playlist_schema.validate(res.text)
