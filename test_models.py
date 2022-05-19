import os
from unittest import TestCase
from models import db, User, Drink, Favorite

os.environ['DATABASE_URL'] = "postgresql:///cap1_test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Tests for User model"""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user = User.register('tester', 'password')
        user_id = 111
        user.id = user_id

        drink = Drink(name = 'drink')
        drink_id = 111
        drink.id = drink_id
        
        db.session.add(drink)
        db.session.commit()

        user = User.query.get(user_id)
        drink = Drink.query.get(drink_id)

        self.user = user
        self.user_id = user_id

        self.drink = drink
        self.drink_id = drink_id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic user model work?"""

        u = User(
            username='thisistest',
            passhash='HASHED_PASSWORD'
        )

        db.session.add(u)
        db.session.commit()

        # User should have no favorites
        self.assertEqual(len(u.favorites), 0)

    def test_user_favorites(self):
        """Can a user add a drink to their favorites list?"""
        self.user.favorites.append(self.drink)
        db.session.commit()

        self.assertEqual(len(self.user.favorites), 1)
        
        self.assertEqual(self.user.favorites[0].id, self.drink_id)

