# -*- coding: utf8 -*-

"""Tests for non-dynamic pages.

:license: AGPL v3, see LICENSE for more details
:copyright: 2014-2016 Joe Doherty

"""

# 3rd party imports
from flask import url_for
# Pjuu imports
from pjuu.auth.backend import create_account, activate
# Test imports
from tests import FrontendTestCase


class PagesTests(FrontendTestCase):
    """Test that the pages are rendered

    """

    def test_logged_out(self):
        """Check the pages work when logged test_logged_out

        """
        # Abouts
        resp = self.client.get(url_for('pages.about'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<!-- menu: not logged in -->', resp.data)
        self.assertIn('<h1>About Us</h1>', resp.data)

        # Terms
        resp = self.client.get(url_for('pages.terms'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<!-- menu: not logged in -->', resp.data)
        self.assertIn('<h1>Terms of Service</h1>', resp.data)

        # Privacy
        resp = self.client.get(url_for('pages.privacy'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<!-- menu: not logged in -->', resp.data)
        self.assertIn('<h1>Privacy</h1>', resp.data)

    def test_logged_in(self):
        """Check the pages work when logged in

        """
        # Let's create a user an login
        user1 = create_account('user1', 'user1@pjuu.com', 'Password')
        # Activate the account
        self.assertTrue(activate(user1))
        # Log the user in
        resp = self.client.post(url_for('auth.signin'), data={
            'username': 'user1',
            'password': 'Password'
        }, follow_redirects=True)

        # About
        resp = self.client.get(url_for('pages.about'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<!-- menu: logged in -->', resp.data)
        self.assertIn('<h1>About Us</h1>', resp.data)

        # Terms
        resp = self.client.get(url_for('pages.terms'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<!-- menu: logged in -->', resp.data)
        self.assertIn('<h1>Terms of Service</h1>', resp.data)

        # Privacy
        resp = self.client.get(url_for('pages.privacy'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<!-- menu: logged in -->', resp.data)
        self.assertIn('<h1>Privacy</h1>', resp.data)
