# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json

from webapp2_extras import securecookie

from gaebusiness.business import CommandList
from pswdclient.manager import FindOrCreateSecrets


class SignDct(CommandList):
    def __init__(self, name, dct):
        self.name = name
        self.dct = dct
        self._find_secret = FindOrCreateSecrets()
        super(SignDct, self).__init__([self._find_secret])

    def do_business(self, stop_on_error=False):
        super(SignDct, self).do_business(stop_on_error)
        secret = self._find_secret.result
        value = json.dumps(self.dct)
        serializer = securecookie.SecureCookieSerializer(str(secret))
        self.result = serializer.serialize(self.name, value)

class RetrieveDct(CommandList):
    def __init__(self, name, signed,max_age):
        self.max_age=max_age
        self.name = name
        self.signed = signed
        self._find_secret = FindOrCreateSecrets()
        super(RetrieveDct, self).__init__([self._find_secret])

    def do_business(self, stop_on_error=False):
        super(RetrieveDct, self).do_business(stop_on_error)
        secret = self._find_secret.result
        serializer = securecookie.SecureCookieSerializer(str(secret))
        data = serializer.deserialize(self.name, self.signed, self.max_age)
        if data:
            self.result = json.loads(data)


class RetrieveUserDetail(CommandList):
    def __init__(self,request,cookie_name='user',max_age=604800):
        signed=request.cookies.get(cookie_name)
        self._retrive_dct=RetrieveDct(cookie_name,signed,max_age)
        super(RetrieveUserDetail,self).__init__([self._retrive_dct])

    def do_business(self, stop_on_error=False):
        super(RetrieveUserDetail,self).do_business(stop_on_error)
        self.result=self._retrive_dct.result

