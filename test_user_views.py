"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py

# questions to consider when writing tests
# 
# When you’re logged in, can you see the follower / following pages for any user?
# When you’re logged out, are you disallowed from visiting a user’s follower / following pages?
# When you’re logged in, can you add a message as yourself?
# When you’re logged in, can you delete a message as yourself?
# When you’re logged out, are you prohibited from adding messages?
# When you’re logged out, are you prohibited from deleting messages?
# When you’re logged in, are you prohibiting from adding a message as another user?
# When you’re logged in, are you prohibiting from deleting a message as another user?


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("abc", "test1@test.com", "password", None)
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.signup("efg", "test2@test.com", "password", None)
        self.u2_id = 884
        self.u2.id = self.u2_id
        self.u3 = User.signup("hij", "test3@test.com", "password", None)
        self.u4 = User.signup("testing", "test4@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_list_user(self):
        """Does it pull up users"""

        with self.client as c:
      
            resp = c.get("/users")

            self.assertEqual(resp.status_code,200)

            html = resp.get_data(as_text=True)

            self.assertIn("<p>@testuser</p>", html)

    def test_user_show(self):
        """Can it pull up a user"""

        with self.client as c:

            resp = c.get(f"/users/{self.testuser.id}")

            self.assertEqual(resp.status_code,200)
            html = resp.get_data(as_text=True)

            self.assertIn('<h4 id="sidebar-username">@testuser</h4>',html)

    def test_show_following(self):
        """Does it show the follow list"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/following")

            self.assertEqual(resp.status_code,200)

    def test_show_followers(self):
        """Does it show the follow list"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/followers")

            self.assertEqual(resp.status_code,200)

    def test_adding_follow(self):
        """Will it add to the follow list"""

        with self.client as c:

            new_user = User.signup(username="testuser2",
                                email="test@test2.com",
                                password="testuser",
                                image_url=None)
            db.session.commit()

            id = new_user.id

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/follow/{id}",follow_redirects=True)

            self.assertEqual(resp.status_code,200)

            html = resp.get_data(as_text=True)

            self.assertIn(f'<a href="/users/{self.testuser.id}/following">1</a>',html)

    def test_deleting_follow(self):
        """Will it add to the follow list"""

        with self.client as c:

            new_user = User.signup(username="testuser2",
                                email="test@test2.com",
                                password="testuser",
                                image_url=None)
            db.session.commit()

            id = new_user.id

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post(f"/users/follow/{id}")

            resp = c.post(f"/users/stop-following/{id}",follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertIn(f'<a href="/users/{self.testuser.id}/following">0</a>',html)

    def test_delete_user(self):
        """will you be able to delete user while logged out?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("users/delete")
            self.assertEqual(resp.location,"http://localhost/signup")

    def test_add_like(self):
        """Can you add likes?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            like = c.post(f"/users/add_like/{self.msg.id}")

            print(like.status_code)

            