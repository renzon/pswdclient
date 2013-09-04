# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import urllib
from google.appengine.api import urlfetch
from gaebusiness.business import Command
from pswdclient.model import LoginEmailSent


class SendLoginEmail(Command):
    def __init__(self, app_id, token, hook, email=None, user_id=None, lang="en_US",
                 url_login='https://pswdless.appspot.com/rest/login'):
        super(SendLoginEmail,self).__init__()
        if email is None and user_id is None:
            raise Exception('at least one of email and user_id should be not None')
        data = {'app_id': app_id, 'token': token}

        if user_id:
            data['user_id'] = user_id
        else:
            data['email'] = email

        if lang:
            data['lang'] = lang
        if lang:
            data['hook'] = hook

        self._post_data = urllib.urlencode(data)
        self._url = url_login

    def set_up(self):
        self._rpc = urlfetch.create_rpc()
        urlfetch.make_fetch_call(self._rpc, self._url, self._post_data, method=urlfetch.POST, validate_certificate=True)

    def do_business(self, stop_on_error=False):
        result = self._rpc.get_result()
        if result.status_code == 200:
            self.result = json.loads(result.content)
        else:
            self.add_error('http_status', result.status_code)
            self.add_error('msg', result.content)

    def commit(self):
        if self.result and 'ticket' in self.result:
            return LoginEmailSent(ticket=self.result['ticket'])


