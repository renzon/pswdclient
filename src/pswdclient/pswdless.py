# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import urllib
from google.appengine.api import urlfetch
from gaebusiness.business import Command, CommandList
from pswdclient.model import LoginEmailSentCertified
from pswdclient.security import SignDct


class SendLoginEmail(Command):
    def __init__(self, app_id, token, hook, email=None, user_id=None, lang="en_US",
                 url_login='https://pswdless.appspot.com/rest/login'):
        super(SendLoginEmail, self).__init__()
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
        self._rpc = urlfetch.create_rpc(deadline=40)
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
            return LoginEmailSentCertified(ticket=self.result['ticket'])


class CertifyLoginWasSent(Command):
    def __init__(self, ticket):
        super(CertifyLoginWasSent, self).__init__()
        self._ticket = ticket
        self._delete_certify = lambda: None

    def set_up(self):
        self._future = LoginEmailSentCertified.find_by_ticket(self._ticket).fetch_async(1, keys_only=True)

    def do_business(self, stop_on_error=False):
        keys = self._future.get_result()
        if keys:
            self.result = True
            future = keys[0].delete_async()
            self._delete_certify = lambda: future.get_result()
        else:
            self.add_error('ticket', 'Invalid Ticket')

    def commit(self):
        self._delete_certify()


class FetchUserDetail(Command):
    def __init__(self, app_id, token, ticket, url_detail):
        super(FetchUserDetail, self).__init__()
        data = {'app_id': app_id, 'token': token, 'ticket': ticket}
        self._post_data = urllib.urlencode(data)
        self._url = url_detail

    def set_up(self):
        self._rpc = urlfetch.create_rpc(deadline=40)
        urlfetch.make_fetch_call(self._rpc, self._url, self._post_data, method=urlfetch.POST, validate_certificate=True)

    def do_business(self, stop_on_error=False):
        result = self._rpc.get_result()
        if result.status_code == 200:
            self.result = json.loads(result.content)
        else:
            self.add_error('http_status', result.status_code)
            self.add_error('msg', result.content)


class LogUserIn(CommandList):
    def __init__(self, app_id, token, ticket, response, cookie_name, url_detail):
        self._response = response
        self._cookie_name = cookie_name
        self.certify_login_was_sent = CertifyLoginWasSent(ticket)
        self.fetch_user_detail = FetchUserDetail(app_id, token, ticket, url_detail)
        super(LogUserIn, self).__init__([self.certify_login_was_sent, self.fetch_user_detail])

    def do_business(self, stop_on_error=True):
        super(LogUserIn, self).do_business(stop_on_error)
        if not self.certify_login_was_sent.errors:
            cmd = SignDct(self._cookie_name, self.fetch_user_detail.result)
            cmd.execute()
            self.result = self.fetch_user_detail.result
            self._signed = cmd.result # for testing purpose
            self._response.set_cookie(self._cookie_name, cmd.result, httponly=True)


