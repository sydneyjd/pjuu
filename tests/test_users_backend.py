# -*- coding: utf8 -*-

"""
Description:
    Tests for the users package inside Pjuu.

Licence:
    Copyright 2014 Joe Doherty <joe@pjuu.com>

    Pjuu is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Pjuu is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Pjuu imports
from pjuu.auth.backend import create_account, delete_account
from pjuu.posts.backend import create_post
from pjuu.users.backend import *
# Test imports
from tests import BackendTestCase


class BackendTests(BackendTestCase):
    """
    This case will test ALL post backend functions.
    """

    def test_get_profile(self):
        """
        Tests that a user's profile representation can be returned
        """
        # Get test user
        user1 = create_account('user1', 'user1@pjuu.com', 'Password')
        # Attempt to get the users repr
        profile = get_profile(user1)
        # Ensure we got a profile
        self.assertIsNotNone(profile)

        # Check all the keys are present
        self.assertEqual(profile.get('_id'), user1)
        self.assertEqual(profile.get('username'), 'user1')
        self.assertEqual(profile.get('email'), 'user1@pjuu.com')
        # Ensure all the injected information is present
        self.assertEqual(profile.get('post_count'), 0)
        self.assertEqual(profile.get('followers_count'), 0)
        self.assertEqual(profile.get('following_count'), 0)

        # Ensure a non-existant profile return None
        self.assertEqual(get_profile(k.NIL_VALUE), None)

    def test_get_user(self):
        """
        Tests that a user's account can be returned
        """
        # Get test user
        user1 = create_account('user1', 'user1@pjuu.com', 'Password')
        # Attempt to get the users repr
        user = get_user(user1)
        # Ensure we got a profile
        self.assertIsNotNone(user)
        # Check all the keys are present
        self.assertEqual(user.get('_id'), user1)
        self.assertEqual(user.get('username'), 'user1')
        self.assertEqual(user.get('email'), 'user1@pjuu.com')
        # Ensure a non-existant user return None
        self.assertEqual(get_user(k.NIL_VALUE), None)

    def test_follow_unfollow_get_followers_following_is_following(self):
        """
        Test everything about following. There is not that much to it to
        deserve 3 seperate methods.
        """
        # Create two test users
        user1 = create_account('user1', 'user1@pjuu.com', 'Password')
        user2 = create_account('user2', 'user2@pjuu.com', 'Password')
        # Ensure is_following() is false atm
        self.assertFalse(is_following(user1, user2))
        self.assertFalse(is_following(user2, user1))
        # Ensure user 1 can follow user 2
        self.assertTrue(follow_user(user1, user2))
        # Ensure the user can't follow them again
        self.assertFalse(follow_user(user1, user2))
        # And visa-versa
        self.assertTrue(follow_user(user2, user1))
        # Ensre the user can't follow them again
        self.assertFalse(follow_user(user2, user1))
        # Ensure the id's are in the Redis sorted sets, followers and following
        self.assertIn(user2, r.zrange(k.USER_FOLLOWING.format(user1), 0, -1))
        self.assertIn(user2, r.zrange(k.USER_FOLLOWERS.format(user1), 0, -1))
        self.assertIn(user1, r.zrange(k.USER_FOLLOWING.format(user2), 0, -1))
        self.assertIn(user1, r.zrange(k.USER_FOLLOWERS.format(user2), 0, -1))
        # Ensure the get_followers and get_following functions return
        # the correct data
        self.assertEqual(len(get_following(user1).items), 1)
        self.assertEqual(len(get_following(user1).items), 1)
        self.assertEqual(len(get_following(user2).items), 1)
        self.assertEqual(len(get_following(user2).items), 1)
        # Ensure the totals are correct
        self.assertEqual(get_following(user1).total, 1)
        self.assertEqual(get_followers(user1).total, 1)
        self.assertEqual(get_following(user2).total, 1)
        self.assertEqual(get_followers(user2).total, 1)

        # Make sure is_following() returns correctly
        self.assertTrue(is_following(user1, user2))
        self.assertTrue(is_following(user2, user1))

        # User 1 unfollow user 2 and ensure the sorted sets are updated
        self.assertTrue(unfollow_user(user1, user2))
        self.assertNotIn(user2,
                         r.zrange(k.USER_FOLLOWING.format(user1), 0, -1))
        self.assertNotIn(user1,
                         r.zrange(k.USER_FOLLOWERS.format(user2), 0, -1))

        # Ensure the user can't unfollow the user again
        self.assertFalse(unfollow_user(user1, user2))
        # Ensure is_following shows correctly
        self.assertFalse(is_following(user1, user2))

        # Test what happens when we delete an account.

        # Ensure user 2 is still following user1
        self.assertTrue(is_following(user2, user1))

        # This should clean
        delete_account(user1)

        # Ensure this has cleaned user2 following list
        self.assertFalse(is_following(user2, user1))

        # Ensure get_followers and get_following return the correct value for
        # user2
        self.assertEqual(len(get_following(user2).items), 0)
        # Ensure the totals are correct
        self.assertEqual(get_following(user2).total, 0)
        self.assertEqual(get_followers(user2).total, 0)
        # Make sure is_following() returns correctly
        self.assertFalse(is_following(user1, user2))
        self.assertFalse(is_following(user2, user1))

        # I don't want to play with the above testing to much. I am adding
        # in a test for self cleaning lists. I am going to reset this test
        # case by manually flushing the Redis database :)
        r.flushdb()
        # Back to normal, I don't like artificially uping the number of tests.

        # Test the self cleaning lists in case there is an issue with Redis
        # during an account deletion. We need 2 new users.
        user1 = create_account('user1', 'user1@pjuu.com', 'Password')
        user2 = create_account('user2', 'user2@pjuu.com', 'Password')

        # Follow each other.
        self.assertTrue(follow_user(user1, user2))
        self.assertTrue(follow_user(user2, user1))

        # Manually delete user1
        m.db.users.remove({'_id': user1})

        # Ensure user1 appears in both user2's followers and following lists
        self.assertIn(user1, r.zrange(k.USER_FOLLOWERS.format(user2), 0, -1))
        self.assertIn(user1, r.zrange(k.USER_FOLLOWING.format(user2), 0, -1))

        # Ensure if we actuallt get the lists from the backend functions user1
        # is not there
        self.assertEqual(get_followers(user2).total, 0)
        self.assertEqual(get_following(user2).total, 0)

    def test_back_feed(self):
        """Test the back feed feature, once a user follows another user it
        places their latest 5 posts on their feed. They will be in chronologic
        order.

        I know that ``back_feed()`` is a posts feature but it is triggered on
        follow.

        """
        user1 = create_account('user1', 'user1@pjuu.com', 'Password')
        user2 = create_account('user2', 'user2@pjuu.com', 'Password')

        # Create 6 test posts ('Test 1' shouldn't be back fed)
        post1 = create_post(user1, 'user1', 'Test 1')
        post2 = create_post(user1, 'user1', 'Test 2')
        post3 = create_post(user1, 'user1', 'Test 3')
        post4 = create_post(user1, 'user1', 'Test 4')
        post5 = create_post(user1, 'user1', 'Test 5')
        post6 = create_post(user1, 'user1', 'Test 6')

        follow_user(user2, user1)

        # Check that the posts are in the feed (we can do this in Redis)
        feed = r.zrevrange(k.USER_FEED.format(user2), 0, -1)

        self.assertNotIn(post1, feed)
        self.assertIn(post2, feed)
        self.assertIn(post3, feed)
        self.assertIn(post4, feed)
        self.assertIn(post5, feed)
        self.assertIn(post6, feed)

    def test_search(self):
        """
        Make sure users can actually find each other.

        This will need a lot more work once we add in a proper search facility
        rather than just the Redis KEYS command
        """
        # Create test user
        create_account('user1', 'user1@pjuu.com', 'Password')
        # Ensure that the user can be found
        self.assertEqual(len(search('user1').items), 1)
        self.assertEqual(search('user1').total, 1)
        # Ensure partial match
        self.assertEqual(len(search('use').items), 1)
        self.assertEqual(search('use').total, 1)
        # Ensure nothing return if no user
        self.assertEqual(len(search('user2').items), 0)
        self.assertEqual(search('user2').total, 0)
        # Ensure no partial if incorrect
        self.assertEqual(len(search('bob').items), 0)
        self.assertEqual(search('bob').total, 0)

        # Create a second test user
        user2 = create_account('user2', 'user2@pjuu.com', 'Password')
        # Ensure the new user can be found
        self.assertEqual(len(search('user2').items), 1)
        self.assertEqual(search('user2').total, 1)
        # Ensure partial match returns both test1/2 users
        self.assertEqual(len(search('use').items), 2)
        self.assertEqual(search('use').total, 2)

        # Delete the account test 2 and try searching again
        # Adding in this test as it has stung us before
        delete_account(user2)
        self.assertEqual(search('test2').total, 0)
        # Done

    def test_alerts(self):
        """
        Tests for the 2 functions which are used on the side to get alerts and
        also test FollowAlert from here.
        """
        # Create 2 test users
        user1 = create_account('user1', 'user1@pjuu.com', 'Password')
        user2 = create_account('user2', 'user2@pjuu.com', 'Password')

        # Ensure that get_alerts pagination object is empty
        self.assertEqual(get_alerts(user1).total, 0)
        self.assertEqual(len(get_alerts(user1).items), 0)

        # Get user 2 to follow user 1
        follow_user(user2, user1)

        # Check that i_has_alerts is True
        self.assertTrue(i_has_alerts(user1))

        # Ensure that there is an alert in the get_alerts
        self.assertEqual(get_alerts(user1).total, 1)
        self.assertEqual(len(get_alerts(user1).items), 1)

        # Check that i_has_alerts is False, we have read them with get_alerts
        self.assertFalse(i_has_alerts(user1))

        # Get the alert and check that the alert is the follow alert
        alert = get_alerts(user1).items[0]
        self.assertTrue(isinstance(alert, FollowAlert))
        # Also check it's still a BaseAlert
        self.assertTrue(isinstance(alert, BaseAlert))
        # Check its from test2
        self.assertEqual(alert.user.get('username'), 'user2')
        self.assertEqual(alert.user.get('email'), 'user2@pjuu.com')
        self.assertIn('has started following you', alert.prettify())

        # Delete test2 and ensure we get no alerts
        delete_account(user2)

        # Ensure the alert is still inside Redis
        self.assertEqual(r.zcard(k.USER_ALERTS.format(user1)), 1)

        # Get the alerts, should be none and should also clear the alert from
        # Redis
        self.assertEqual(get_alerts(user1).total, 0)
        self.assertEqual(len(get_alerts(user1).items), 0)
        self.assertEqual(r.zcard(k.USER_ALERTS.format(user1)), 0)

        # Do the same as above to ensure we can delete an alert ourselves
        # Create another user
        user3 = create_account('user3', 'user3@pjuu.com', 'Password')

        follow_user(user1, user3)

        # Check the alerts are there
        alert = get_alerts(user3).items[0]
        self.assertTrue(isinstance(alert, FollowAlert))
        # Also check it's still a BaseAlert
        self.assertTrue(isinstance(alert, BaseAlert))
        # Check its from test2
        self.assertEqual(alert.user.get('username'), 'user1')
        self.assertEqual(alert.user.get('email'), 'user1@pjuu.com')
        self.assertIn('has started following you', alert.prettify())

        # Delete the alert with aid from the alert
        delete_alert(user3, alert.alert_id)

        # Get the alerts and ensure the list is empty
        self.assertEqual(get_alerts(user3).total, 0)
        self.assertEqual(len(get_alerts(user3).items), 0)
        self.assertEqual(r.zcard(k.USER_ALERTS.format(user3)), 0)

        # Unfollow the user3 and then follow them again
        unfollow_user(user1, user3)
        follow_user(user1, user3)

        alert = get_alerts(user3).items[0]
        self.assertIn('has started following you', alert.prettify())

        # Manually delete the alert
        r.delete(k.ALERT.format(alert.alert_id))

        # Get the alerts again and ensure the length is 0
        # Ensure that the alert is not pulled down
        alerts = get_alerts(user3)
        self.assertEqual(len(alerts.items), 0)

        # Get alerts for a non-existant user
        # This will not fail but will have an empty pagination
        alerts = get_alerts(k.NIL_VALUE)
        self.assertEqual(len(alerts.items), 0)

        # Done for now
