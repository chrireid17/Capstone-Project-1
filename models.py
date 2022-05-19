from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import String

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database"""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User Model."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String, unique=True, nullable=False)
    passhash = db.Column(db.String, nullable=False)

    favorites = db.relationship('Drink', secondary='favorites')

    @classmethod
    def register(cls, username, password):
        """Register a user and add them to the database"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, passhash=hashed_pwd)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Finds user with matching username and password. If user is found and 
        password is correct return user, else return False. 
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.passhash, password)
            if is_auth:
                return user
        
        else:
            return False
class Drink(db.Model):
    """Drink Model."""

    __tablename__ = 'drinks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.ARRAY(String, dimensions=1))
    measurements = db.Column(db.ARRAY(String, dimensions=1))
    instructions = db.Column(db.Text)
    img_url = db.Column(db.String)
    api_id = db.Column(db.String)

    favorites = db.relationship('User', secondary='favorites')

    def __repr__(self):
        return f'<Drink #{self.id}: {self.name}, {self.ingredients}, {self.measurements}, {self.instructions}, {self.img_url}, {self.api_id}>'

class Favorite(db.Model):
    """Model for relationship between a drink and a user."""

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    drink_id = db.Column(db.Integer, db.ForeignKey('drinks.id'))
