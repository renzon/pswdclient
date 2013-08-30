# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.api import memcache
from os import urandom
from gaebusiness.business import Command
from pswdclient.model import SignSecret

_SIGN_CACHE_KEY = SignSecret.__name__


def _generate_secret():
    return urandom(16).encode("hex")


class FindOrCreateSecrets(Command):
    def __init__(self):
        super(FindOrCreateSecrets, self).__init__()
        self._to_commit = []
        self._future = None

    def set_up(self):
        try:
            self.result = memcache.get(_SIGN_CACHE_KEY)
        except Exception:
            pass # If memcache fails, do nothing
        if self.result is None:
            self._future = SignSecret.find_last().fetch_async(2)


    def do_business(self, stop_on_error=False):
        if self._future:
            secrets = self._future.get_result()
            if secrets:
                self.result = [sign.secret for sign in secrets]
            else:
                secret = _generate_secret()
                self.result = [secret]
                self._to_commit = [SignSecret(secret=secret)]
            memcache.add(_SIGN_CACHE_KEY, self.result)

    def commit(self):
        return self._to_commit


class RenewSecrets(Command):
    def set_up(self):
        self._find_secret = FindOrCreateSecrets()
        self._find_secret.set_up()

    def do_business(self, stop_on_error=False):
        self._find_secret.do_business()

    def commit(self):
        secret = _generate_secret()
        to_commit = [SignSecret(secret=secret)]
        memcache.add(_SIGN_CACHE_KEY, [self._find_secret.result, secret])
        to_commit.extend(self._find_secret.commit())
        return to_commit


class RevokeSecrets(Command):
    def do_business(self, stop_on_error=False):
        self._secrets=[_generate_secret(),_generate_secret()]
        memcache.add(_SIGN_CACHE_KEY,self._secrets)

    def commit(self):
        return [SignSecret(secret=s) for s in self._secrets]



