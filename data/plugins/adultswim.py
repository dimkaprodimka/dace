#-plugin-sig:mnGjaVbAwSGZI2nO/CVe/3mtXUXo0h0kId8VNFgdXc8HLZRHDedJ3PpoaBfYH1ucIobNGuuCS9si7+h5H9cYGK/5FEM9iSgfdMLlGzU7Cnxs48JtcfDKSH5kIPmMxMjVWwfMt86BGg2O6rSvtQS/rqrU98SIz+8fVktuMZyBYHOjkufvPuJP49liQjdDX/+7tV/NVGCUChpGruIZc30Mu8qNypHWtg0OhiELkKO4Nzm0J9wng9PVyNOi5//aKAJ995x5Lll5+BPMJO5rtARd2pQQSs4Uua6EFglvsov0kqT52tlz1T/dFL5L5+SDWnM/glxaMjkaicxtp8fi1AR0bQ==
import logging
import re

from ACEStream.PluginsContainer.streamlink.compat import urlparse, urlunparse
from ACEStream.PluginsContainer.streamlink.exceptions import PluginError
from ACEStream.PluginsContainer.streamlink.plugin import Plugin
from ACEStream.PluginsContainer.streamlink.plugin.api import validate
from ACEStream.PluginsContainer.streamlink.stream import HLSStream
from ACEStream.PluginsContainer.streamlink.utils import parse_json

log = logging.getLogger(__name__)


class AdultSwim(Plugin):
    token_url = 'https://token.ngtv.io/token/token_spe'
    video_data_url = 'https://www.adultswim.com/api/shows/v1/media/{0}/desktop'

    app_id_js_url_re = re.compile(
        r'''<script src="([^"]*asvp\..*?\.bundle\.js)">'''
    )

    app_id_re = re.compile(
        r'''CDN_TOKEN_APP_ID="(.*?)"'''
    )

    json_data_re = re.compile(
        r'''<script id="__NEXT_DATA__" type="application/json">({.*})</script>'''
    )

    truncate_url_re = re.compile(r'''(.*)/\w+/?''')

    url_re = re.compile(
        r'''https?://(?:www\.)?adultswim\.com
        /(streams|videos)
        (?:/([^/]+))?
        (?:/([^/]+))?
        ''', re.VERBOSE,
    )

    _api_schema = validate.Schema({
        'media': {
            'desktop': {
                validate.text: {
                    'url': validate.url()
                }
            }
        }},
        validate.get('media'),
        validate.get('desktop'),
        validate.filter(lambda k, v: k in ['unprotected', 'bulkaes'])
    )

    _stream_data_schema = validate.Schema({
        'props': {'__REDUX_STATE__': {'streams': [{
            'id': validate.text,
            'stream': validate.text,
        }]}}},
        validate.get('props'),
        validate.get('__REDUX_STATE__'),
        validate.get('streams'),
    )

    _token_schema = validate.Schema(
        validate.any(
            {'auth': {'token': validate.text}},
            {'auth': {'error': {'message': validate.text}}},
        ),
        validate.get('auth'),
    )

    _video_data_schema = validate.Schema({
        'props': {'pageProps': {'__APOLLO_STATE__': {
            validate.text: {
                validate.optional('id'): validate.text,
                validate.optional('slug'): validate.text,
            }
        }}}},
        validate.get('props'),
        validate.get('pageProps'),
        validate.get('__APOLLO_STATE__'),
        validate.filter(lambda k, v: k.startswith('Video:')),
    )

    @classmethod
    def can_handle_url(cls, url):
        match = AdultSwim.url_re.match(url)
        return match is not None

    def _get_stream_data(self, id):
        res = self.session.http.get(self.url)
        m = self.json_data_re.search(res.text)
        if m and m.group(1):
            streams = parse_json(m.group(1), schema=self._stream_data_schema)
        else:
            raise PluginError("Failed to get json_data")

        for stream in streams:
            if 'id' in stream:
                if id == stream['id'] and 'stream' in stream:
                    return stream['stream']

    def _get_video_data(self, slug):
        m = self.truncate_url_re.search(self.url)
        if m and m.group(1):
            log.debug("Truncated URL={0}".format(m.group(1)))
        else:
            raise PluginError("Failed to truncate URL")

        res = self.session.http.get(m.group(1))
        m = self.json_data_re.search(res.text)
        if m and m.group(1):
            videos = parse_json(m.group(1), schema=self._video_data_schema)
        else:
            raise PluginError("Failed to get json_data")

        for video in videos:
            if 'slug' in videos[video]:
                if slug == videos[video]['slug'] and 'id' in videos[video]:
                    return videos[video]['id']

    def _get_token(self, path):
        res = self.session.http.get(self.url)
        m = self.app_id_js_url_re.search(res.text)
        app_id_js_url = m and m.group(1)
        if not app_id_js_url:
            raise PluginError("Could not determine app_id_js_url")
        log.debug("app_id_js_url={0}".format(app_id_js_url))

        res = self.session.http.get(app_id_js_url)
        m = self.app_id_re.search(res.text)
        app_id = m and m.group(1)
        if not app_id:
            raise PluginError("Could not determine app_id")
        log.debug("app_id={0}".format(app_id))

        res = self.session.http.get(self.token_url, params=dict(
            format='json',
            appId=app_id,
            path=path,
        ))

        token_data = self.session.http.json(res, schema=self._token_schema)
        if 'error' in token_data:
            raise PluginError(token_data['error']['message'])

        return token_data['token']

    def _get_streams(self):
        url_match = self.url_re.match(self.url)
        url_type, show_name, episode_name = url_match.groups()

        if url_type == 'streams' and not show_name:
            url_type = 'live-stream'
        elif not show_name:
            raise PluginError("Missing show_name for url_type: {0}".format(
                url_type,
            ))

        log.debug("URL type={0}".format(url_type))

        if url_type == 'live-stream':
            video_id = self._get_stream_data(url_type)
        elif url_type == 'streams':
            video_id = self._get_stream_data(show_name)
        elif url_type == 'videos':
            if show_name is None or episode_name is None:
                raise PluginError(
                    "Missing show_name or episode_name for url_type: {0}".format(
                        url_type,
                    )
                )
            video_id = self._get_video_data(episode_name)
        else:
            raise PluginError("Unrecognised url_type: {0}".format(url_type))

        if video_id is None:
            raise PluginError("Could not find video_id")
        log.debug("Video ID={0}".format(video_id))

        res = self.session.http.get(self.video_data_url.format(video_id))

        url_data = self.session.http.json(res, schema=self._api_schema)
        if 'unprotected' in url_data:
            url = url_data['unprotected']['url']
        elif 'bulkaes' in url_data:
            url_parsed = urlparse(url_data['bulkaes']['url'])
            token = self._get_token(url_parsed.path)
            url = urlunparse((
                url_parsed.scheme,
                url_parsed.netloc,
                url_parsed.path,
                url_parsed.params,
                "{0}={1}".format('hdnts', token),
                url_parsed.fragment,
            ))
        else:
            raise PluginError("Could not find a usable URL in url_data")

        log.debug("URL={0}".format(url))

        return HLSStream.parse_variant_playlist(self.session, url)


__plugin__ = AdultSwim
