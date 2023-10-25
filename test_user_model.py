"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

# questions to think about when writing test
# 
# Does the repr method work as expected?
# Does is_following successfully detect when user1 is following user2?
# Does is_following successfully detect when user1 is not following user2?
# Does is_followed_by successfully detect when user1 is followed by user2?
# Does is_followed_by successfully detect when user1 is not followed by user2?
# Does User.create successfully create a new user given valid credentials?
# Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
# Does User.authenticate successfully return a user when given a valid username and password?
# Does User.authenticate fail to return a user when the username is invalid?
# Does User.authenticate fail to return a user when the password is invalid?


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# sample data
USER_DATA = {
    "email" : "sample@sample.com",
    "username" : "sampleuser",
    "password" : "HASHED_PASSWORD"
}

USER_DATA_2 = {
    "email" : "sample2@sample2.com",
    "username" : "sampleuser2",
    "password" : "HASHED_PASSWORD"
}

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        sample = User(**USER_DATA)
        sample2 = User(**USER_DATA_2)
        db.session.add(sample)
        db.session.add(sample2)
        db.session.commit()

        db.session.refresh(sample)

        self.sample1 = sample
        self.sample2 = sample2

        self.client = app.test_client()

    def tearDown(self):
        """deletes the test data"""
        res = super().tearDown()
        db.session.rollback()
        return res
        

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """does __repr__ work?"""
        self.assertTrue(self.sample1)

    def test_is_following(self):
        """Does following work?"""
        self.sample1.following.append(self.sample2)

        self.assertEqual(User.is_following(self.sample1,self.sample2), 1)
        self.assertEqual(User.is_following(self.sample2,self.sample1), 0)

    def test_is_followed(self):
        """Does followed by work?"""
        self.sample1.followers.append(self.sample2)

        self.assertEqual(User.is_followed_by(self.sample1,self.sample2), 1)
        self.assertEqual(User.is_followed_by(self.sample2,self.sample1), 0)

    def test_signup(self):
        """Does sign up work?"""

        user = User.signup("newtest","new@test.com","testcode","testimage")
        db.session.commit()

        self.assertEqual(user.username,"newtest")
        self.assertEqual(user.email,"new@test.com")
        self.assertEqual(user.image_url,"testimage")
        self.assertNotEqual(user.password, "password")
        self.assertEqual(User.authenticate(user.username,"testcode"),user)

    def test_failed_username(self):
        """Will username fail?"""
        fail = User.signup(None, "test@test.com", "password", None)
        uid = 66
        fail.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_failed_email_signup(self):
        """Will email fail?"""
        fail = User.signup("testtest", None, "password", None)
        uid = 66
        fail.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_failed_password_signup(self):
        """Will password fail?"""
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)

    def test_edit(self):
        """Does the edit work?"""
        user_edit = User.edit(self.sample1.username,"newsample","good@email.com","newimage","newheader","I edited")
        db.session.commit()
        
        self.assertEqual(self.sample1.username,"newsample")
        self.assertEqual(self.sample1.email,"good@email.com")
        self.assertEqual(self.sample1.image_url,"newimage")
        self.assertEqual(self.sample1.header_image_url,"newheader")
        self.assertEqual(self.sample1.password,"HASHED_PASSWORD")

    def test_edit_username(self):
        """Does the edit work?"""
        user_edit = User.edit(self.sample1.username,"newsample",None,None,None,None)
        db.session.commit()
        
        self.assertEqual(self.sample1.username,"newsample")
        self.assertEqual(self.sample1.email,"sample@sample.com")

    def test_edit_email(self):
        """Does the edit work?"""
        user_edit = User.edit(self.sample1.username,None,"new@sample.com",None,None,None)
        db.session.commit()
        
        self.assertEqual(self.sample1.email,"new@sample.com")

    def test_edit_image_url(self):
        """Does the edit work?"""
        user_edit = User.edit(self.sample1.username,None,None,"newsample",None,None)
        db.session.commit()
        
        self.assertEqual(self.sample1.image_url,"newsample")

    def test_edit_header_image(self):
        """Does the edit work?"""
        user_edit = User.edit(self.sample1.username,None,None,None,"newsample",None)
        db.session.commit()
        
        self.assertEqual(self.sample1.header_image_url,"newsample")

    def test_edit_bio(self):
        """Does the edit work?"""
        user_edit = User.edit(self.sample1.username,None,None,None,None,"newsample")
        db.session.commit()
        
        self.assertEqual(self.sample1.bio,"newsample")