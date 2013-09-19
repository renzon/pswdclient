# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
import urllib
from google.appengine.api import urlfetch
from base import GAETestCase
from mock import Mock
from pswdclient.model import LoginEmailSentCertified
from pswdclient.pswdless import SendLoginEmail, CertifyLoginWasSent, FetchUserDetail, LogUserIn
from pswdclient import pswdless, facade


class SendLoginEmailTests(GAETestCase):
    def test_success(self):
        rpc = Mock()
        result = Mock()
        result.status_code = 200
        result.content = '{"ticket":"123456"}'
        rpc.get_result = Mock(return_value=result)
        pswdless.urlfetch.create_rpc = Mock(return_value=rpc)
        fetch = Mock()
        pswdless.urlfetch.make_fetch_call = fetch
        post_params = {'app_id': 1, 'token': '2', 'hook': 'http://yourhooke.com', 'email': 'foo@bar.com',
                       'lang': "pt_BR"}
        url = 'https://pswdless.appspot.com/rest/login'
        send_login_params = {'url_login': url}
        send_login_params.update(post_params)

        send_login = facade.send_login_email(**send_login_params)
        send_login.execute()
        self.assertDictEqual({'ticket': "123456"}, send_login.result)
        les_model = LoginEmailSentCertified.find_by_ticket("123456").get()
        self.assertEqual("123456", les_model.ticket)
        fetch.assert_called_once_with(rpc, url, urllib.urlencode(post_params), method=urlfetch.POST,
                                      validate_certificate=True)


    def test_error(self):
        rpc = Mock()
        result = Mock()
        result.status_code = 400
        result.content = 'error'
        rpc.get_result = Mock(return_value=result)
        pswdless.urlfetch.create_rpc = Mock(return_value=rpc)
        pswdless.urlfetch.make_fetch_call = Mock()
        send_login = SendLoginEmail(1, 1, "h", user_id='5')
        send_login.execute()
        self.assertDictEqual({'http_status': 400, 'msg': 'error'}, send_login.errors)


    def test_email_and_id(self):
        self.assertRaises(Exception, SendLoginEmail, 1, 1, 'h')


class CertifyLoginWasSentTests(GAETestCase):
    def test_login_not_sent(self):
        cmd = CertifyLoginWasSent('someticket')
        cmd.execute()
        self.assertIsNone(cmd.result)
        self.assertDictEqual({'ticket': 'Invalid Ticket'}, cmd.errors)

    def test_login_sent(self):
        valid_ticket = 'valid_ticket'
        LoginEmailSentCertified(ticket=valid_ticket).put()
        cmd = CertifyLoginWasSent(valid_ticket)
        cmd.execute()
        self.assertIsNotNone(cmd.result)
        self.assertDictEqual({}, cmd.errors)
        self.assertIsNone(LoginEmailSentCertified.find_by_ticket(valid_ticket).get(), 'Certified should be erased')


class FetchUserDetailTests(unittest.TestCase):
    def test_success(self):
        rpc = Mock()
        result = Mock()
        result.status_code = 200
        result.content = '{"id":"123456","email":"foo@bar.com"}'
        rpc.get_result = Mock(return_value=result)
        pswdless.urlfetch.create_rpc = Mock(return_value=rpc)
        fetch = Mock()
        pswdless.urlfetch.make_fetch_call = fetch
        post_params = {'app_id': '1', 'token': '2', 'ticket': '3'}
        url_detail = 'https://pswdless.appspot.com/rest/detail'
        params = {'url_detail': url_detail}
        params.update(post_params)

        cmd = FetchUserDetail(**params)
        cmd.execute()
        self.assertDictEqual({"id": "123456", "email": "foo@bar.com"}, cmd.result)
        fetch.assert_called_once_with(rpc, url_detail, urllib.urlencode(post_params), method=urlfetch.POST,
                                      validate_certificate=True)


class LogUserInTests(GAETestCase):
    def test_success(self):
        # Setting up valid ticket
        valid_ticket = 'valid_ticket'
        LoginEmailSentCertified(ticket=valid_ticket).put()

        #setting user data return
        rpc = Mock()
        result = Mock()
        result.status_code = 200
        result.content = '{"id":"123456","email":"foo@bar.com"}'
        rpc.get_result = Mock(return_value=result)
        pswdless.urlfetch.create_rpc = Mock(return_value=rpc)
        fetch = Mock()
        pswdless.urlfetch.make_fetch_call = fetch
        post_params = {'app_id': '1', 'token': '2', 'ticket': valid_ticket}
        url_detail = 'https://pswdless.appspot.com/rest/detail'
        params = {'url_detail': url_detail}
        params.update(post_params)
        response = Mock()
        response.set_cookie = Mock()
        cmd = LogUserIn(cookie_name='user', response=response, **params)
        cmd.execute()
        self.assertDictEqual({"id": "123456", "email": "foo@bar.com"}, cmd.result)
        fetch.assert_called_once_with(rpc, url_detail, urllib.urlencode(post_params), method=urlfetch.POST,
                                      validate_certificate=True)
        self.assertIsNone(LoginEmailSentCertified.find_by_ticket(valid_ticket).get())
        response.set_cookie.assert_called_once_with('user', cmd._signed, httponly=True)

class LogUserOutTests(unittest.TestCase):
    def test_success(self):
        resp=Mock()
        cmd=facade.log_user_out(resp,'user')
        cmd.execute()
        resp.delete_cookie.assert_called_once_with('user')

