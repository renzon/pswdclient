# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import urllib
from google.appengine.api import urlfetch
from base import GAETestCase
from mock import Mock
from pswdclient.model import LoginEmailSent
from pswdclient.pswdless import SendLoginEmail
from pswdclient import pswdless


class SendLoginEmailTests(GAETestCase):
    def test_success(self):
        rpc = Mock()
        result = Mock()
        result.status_code = 200
        result.content = '{"ticket":"123456"}'
        rpc.get_result = Mock(return_value=result)
        pswdless.urlfetch.create_rpc = Mock(return_value=rpc)
        fetch=Mock()
        pswdless.urlfetch.make_fetch_call =fetch
        post_params={ 'app_id':1, 'token':'2', 'hook':'http://yourhooke.com', 'email':'foo@bar.com', 'lang':"pt_BR"}
        url='https://pswdless.appspot.com/rest/login'
        send_login_params={'url_login':url}
        send_login_params.update(post_params)

        send_login = SendLoginEmail(**send_login_params)
        send_login.execute()
        self.assertDictEqual({'ticket': "123456"}, send_login.result)
        les_model=LoginEmailSent.find_by_ticket("123456").get()
        self.assertEqual("123456",les_model.ticket)
        fetch.assert_called_once_with(rpc,url,urllib.urlencode(post_params),method=urlfetch.POST,validate_certificate=True)


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
        self.assertDictEqual({'http_status': 400,'msg':'error'}, send_login.errors)


    def test_email_and_id(self):
        self.assertRaises(Exception, SendLoginEmail, 1, 1, 'h')
