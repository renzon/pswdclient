# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from base import GAETestCase
from pswdclient.model import SignSecret
from pswdclient.manager import FindOrCreateSecrets, RenewSecrets, RevokeSecrets


class TestSignSecret(GAETestCase):
    def test_find_or_create(self):
        # Secret creation
        command=FindOrCreateSecrets()
        command.execute()
        sign_secrets= SignSecret.query().order(-SignSecret.creation).fetch()
        self.assertEqual(1,len(sign_secrets))

        # Last secret reuse

        command2=FindOrCreateSecrets()
        command2.execute()
        sign_secrets= SignSecret.query().order(-SignSecret.creation).fetch()
        self.assertEqual(1,len(sign_secrets))
        self.assertIsNotNone(command.result)
        self.assertEqual(command.result,command2.result)

class TestRenewSecrets(GAETestCase):
    def test_simple_without_invalidation(self):
        find_command=FindOrCreateSecrets()
        find_command.execute()
        RenewSecrets().execute()
        find_after_renew=FindOrCreateSecrets()
        find_after_renew.execute()
        self.assertEqual(2,len(find_after_renew.result))
        self.assertEqual(find_command.result[0],find_after_renew[1])
        RenewSecrets().execute()
        find_after_renew2=FindOrCreateSecrets()
        find_after_renew2.execute()
        self.assertEqual(2,len(find_after_renew2.result))
        self.assertEqual(find_after_renew.result[0],find_after_renew[1])
        self.assertNotEqual(find_after_renew.result[1],find_after_renew[0])

    def test_simple_with_invalidation(self):
        find_command=FindOrCreateSecrets()
        find_command.execute()
        RevokeSecrets(True).execute()
        find_after_renew=FindOrCreateSecrets()
        find_after_renew.execute()
        self.assertEqual(2,len(find_after_renew.result))
        self.assertNotEqual(find_command.result[0],find_after_renew[1])
        RevokeSecrets(True).execute()
        find_after_renew2=FindOrCreateSecrets()
        find_after_renew2.execute()
        self.assertEqual(2,len(find_after_renew2.result))
        self.assertNotEqual(find_after_renew.result[1],find_after_renew[0])
        self.assertNotEqual(find_after_renew.result[0],find_after_renew[0])
        self.assertNotEqual(find_after_renew.result[0],find_after_renew[1])
        self.assertNotEqual(find_after_renew.result[1],find_after_renew[1])




