# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pswdclient.manager import RenewSecrets
from pswdclient.security import SignDctCookie, RetrieveDct


def sign_dct(name, dct):
    '''
    Returns a command with dict coded as a signer json
    '''
    return SignDctCookie(name,dct)


def retrieve_dct(name, signed, max_age=604800):
    '''
    Returns the dct on result contained on the signed string coded if it is valid.
     The content can be invalid by someone trying to fake it or because it is above mas age.
     max_age in seconds. Default seven days
    '''
    return RetrieveDct(name,signed,max_age)


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
    return RenewSecrets()
