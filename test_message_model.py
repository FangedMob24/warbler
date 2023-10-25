# run these tests like:
#
#    python -m unittest test_message_model.py

import os
from unittest import TestCase
from sqlalchemy import exc
from datetime import datetime

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

class MessageModelTestCase(TestCase):
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
    
    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="testing",
            timestamp="2023-10-24 22:35:27",
            user_id=self.sample1.id
        )

        db.session.add(m)
        db.session.commit()

        # Message should be connected to the user
        self.assertEqual(len(self.sample1.messages), 1)
        # Should have a timestamp
        self.assertTrue(m.timestamp)
        # Checking the message
        self.assertEqual(m.text,"testing")

    def test_failed_text(self):
        "Will the model reject if no text is typed"
        
        m = Message(
            text=None,
            timestamp="2023-10-24 22:35:27",
            user_id=self.sample1.id
        )

        db.session.add(m)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_default_timestamp(self):
        "Should have a timestamp by default"
        
        m = Message(
            text="testing timestamp",
            timestamp=None,
            user_id=self.sample1.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertTrue(m.timestamp)

    def test_failed_user(self):
        "Will the model reject if no text is typed"
        
        m = Message(
            text="testing user_id",
            timestamp="2023-10-24 22:35:27",
            user_id=None
        )

        db.session.add(m)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()