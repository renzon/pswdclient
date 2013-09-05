# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pswdclient.manager import RenewSecrets, RevokeSecrets
from pswdclient.pswdless import SendLoginEmail, LogUserIn
from pswdclient.security import SignDct, RetrieveDct, RetrieveUserDetail


def logged_user(request, cookie_name='user',max_age=604800):
    '''
    Extract the user dict data from cookie or None if the data is invalid.
    Returns a command containing the user data ons its result attribute
    '''
    return RetrieveUserDetail(request, cookie_name='user',max_age=604800)


def log_user_in(app_id, token, ticket, response, cookie_name='user',
                url_detail='https://pswdless.appspot.com/rest/detail'):
    '''
    Log the user in setting the user data dictionary in cookie
    Returns a command containing the user data dict on its result attribute or None in a invalid cenario
    '''
    return LogUserIn(app_id, token, ticket, response, cookie_name, url_detail)


def send_login_email(self, app_id, token, hook, email=None, user_id=None, lang="en_US",
                     url_login='https://pswdless.appspot.com/rest/login'):
    '''
    Contact password-less server to send user a email containing the login link
    '''
    return SendLoginEmail(self, app_id, token, hook, email, user_id, lang, url_login)


def sign_dct(name, dct):
    '''
    Returns a command with dict coded as a signer json
    '''
    return SignDct(name, dct)


def retrieve_dct(name, signed, max_age=604800):
    '''
    Returns the dct on result contained on the signed string coded if it is valid.
     The content can be invalid by someone trying to fake it or because it is above mas age.
     max_age in seconds. Default seven days
    '''
    return RetrieveDct(name, signed, max_age)


def renew():
    '''
    Returns a command that when executed, renews the secret.
    By secret renewing, the security is improved. A cron can be used to renew it with frequency.
    The last secret will be still valid, but the new one will be used to sign new itens.
    Once the sign has expire date, the old secret will be changed to new one gradually
    '''
    return RenewSecrets()


def revoke():
    '''
    Returns a command that when executed, revoke the secrets and create new ones.
    Works like renew, but it invalidates the last secret so content signed with it are not allowed
    Use this when the secret is compromised
    '''
    return RevokeSecrets()
