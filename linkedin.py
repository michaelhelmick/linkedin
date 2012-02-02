#!/usr/bin/evn python

""" LinkedIn """

__author__ = 'Mike Helmick <mikehelmick@me.com>'
__version__ = '0.1.2'

import urllib

try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl

import oauth2 as oauth
import httplib2

try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        try:
            from django.utils import simplejson as json
        except ImportError:
            raise ImportError('A json library is required to use this python library. Lol, yay for being verbose. ;)')


class LinkedinAPIError(Exception): pass
class LinkedinAuthError(LinkedinAPIError): pass


class LinkedinAPI(object):
    def __init__(self, api_key=None, api_secret=None, oauth_token=None, oauth_token_secret=None, headers=None, client_args=None, callback_url=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.oauth_token = oauth_token
        self.oauth_secret = oauth_token_secret
        self.callback_url = callback_url

        # Authentication URLs
        self.request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken'
        self.access_token_url = 'https://api.linkedin.com/uas/oauth/accessToken'
        self.authorize_url = 'https://api.linkedin.com/uas/oauth/authorize'

        if self.callback_url:
            self.request_token_url = '%s?oauth_callback=%s' % (self.request_token_url, self.callback_url)

        self.api_base = 'http://api.linkedin.com'
        self.api_version = 'v1'
        self.api_url = '%s/%s/' % (self.api_base, self.api_version)

        # If there's headers, set them. If not, lets
        self.headers = headers
        if self.headers is None:
            self.headers = {'User-agent': 'Linkedin %s' % __version__}

        # ALL requests will be json. Enforcing it here...
        self.headers.update({'x-li-format': 'json',
                             'Content-Type': 'application/json'})

        self.consumer = None
        self.token = None

        client_args = client_args or {}

        # See if they're authenticating for the first or if they already have some tokens.
        # http://michaelhelmick.com/tokens.jpg
        if self.api_key is not None and self.api_secret is not None:
            self.consumer = oauth.Consumer(key=self.api_key, secret=self.api_secret)

        if self.oauth_token is not None and self.oauth_secret is not None:
            self.token = oauth.Token(key=oauth_token, secret=oauth_token_secret)

        if self.consumer is not None and self.token is not None:
            # Authenticated
            self.client = oauth.Client(self.consumer, self.token, **client_args)
        elif self.consumer is not None:
            # Authenticating
            self.client = oauth.Client(self.consumer, **client_args)
        else:
            # Unauthenticated requests (for LinkedIn calls available to public)
            self.client = httplib2.Http(**client_args)

    def get_authentication_tokens(self):
        """ So, you want to get an authentication url?

            l = LinkedinAPI(YOUR_CONFIG)
            auth_props = l.get_authentication_tokens()
            auth_url = auth_props['auth_url']
            print auth_url
        """

        resp, content = self.client.request(self.request_token_url, 'GET')

        status = int(resp['status'])
        if status != 200:
            raise LinkedinAuthError('There was a problem authenticating you. Error: %s, Message: %s' % (status, content))

        request_tokens = dict(parse_qsl(content))

        auth_url_params = {
            'oauth_token': request_tokens['oauth_token'],
        }

        request_tokens['auth_url'] = self.authorize_url + '?' + urllib.urlencode(auth_url_params)

        return request_tokens

    def get_access_token(self, oauth_verifier):
        """ After being returned from the callback, call this.

            l = LinkedinAPI(YOUR_CONFIG)
            authorized_tokens = l.get_access_token(oauth_verifier)
            oauth_token = authorized_tokens['oauth_token']
            oauth_token_secret = authorized_tokens['oauth_token_secret']
        """

        resp, content = self.client.request('%s?oauth_verifier=%s' % (self.access_token_url, oauth_verifier), 'GET')
        return dict(parse_qsl(content))

    def api_request(self, endpoint, method='GET', fields='', params={}):
        url = self.api_url + endpoint

        if fields:
            url = '%s:(%s)' % (url, fields)

        if method == 'POST':
            resp, content = self.client.request(url, 'POST', body=json.dumps(params), headers=self.headers)

            # As far as I've seen, all POSTs return a 201 and NO body -.-
            # So, we'll just return true if it's a post and returns 201

            # This will catch a successful post, but continue and throw
            # an error if it wasn't successful.
            if 'status' in resp and int(resp['status']) == 201:
                return True
        else:
            resp, content = self.client.request('%s?%s' % (url, urllib.urlencode(params)), 'GET', headers=self.headers)

        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            raise LinkedinAPIError('Content is not valid JSON, unable to be decoded.')

        status = int(resp['status'])
        if status < 200 or status >= 300:
            raise LinkedinAPIError('Error Code: %d, Message: %s' % (status, content['message']))

        return content

    def get(self, endpoint, fields='', params=None):
        params = params or {}
        return self.api_request(endpoint, fields=fields, params=params)

    def post(self, endpoint, fields='', params=None):
        params = params or {}
        return self.api_request(endpoint, method='POST', fields=fields, params=params)
