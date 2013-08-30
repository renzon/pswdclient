# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import time
from base import GAETestCase
from pswdclient.security import SignDctCookie, RetrieveDct


class SignTests(GAETestCase):
    def test_sign_and_retrive(self):
        dct={'a':'asdfsafdsdf','id':4}
        name='somevalue'
        sign=SignDctCookie(name, dct)
        sign.execute()
        self.assertIsNotNone(sign.result)
        retrieve=RetrieveDct(name,sign.result,100)
        retrieve.execute()
        self.assertDictEqual(dct,retrieve.result)

    def test_expired(self):
        dct={'a':'asdfsafdsdf','id':4}
        name='somevalue'
        sign=SignDctCookie(name, dct)
        sign.execute()
        self.assertIsNotNone(sign.result)
        retrieve=RetrieveDct(name,sign.result,1)
        time.sleep(2)
        retrieve.execute()
        self.assertIsNone(retrieve.result)

    def test_modified_cookie(self):
        dct={'a':'asdfsafdsdf','id':4}
        name='somevalue'
        sign=SignDctCookie(name, dct)
        sign.execute()
        self.assertIsNotNone(sign.result)
        retrieve=RetrieveDct(name,sign.result[1:],100)
        retrieve.execute()
        self.assertIsNone(retrieve.result)

