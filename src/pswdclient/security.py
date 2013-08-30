# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json

from webapp2_extras import securecookie

from gaebusiness.business import CommandList
from pswdclient.manager import FindOrCreateSecrets


class SignDctCookie(CommandList):
    def __init__(self, name, dct):
        self.name = name
        self.dct = dct
        self._find_secret = FindOrCreateSecrets()
        super(SignDctCookie, self).__init__([self._find_secret])

    def do_business(self, stop_on_error=False):
        super(SignDctCookie, self).do_business(stop_on_error)
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




