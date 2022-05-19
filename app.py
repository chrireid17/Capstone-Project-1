from crypt import methods
from os import nice
from click import password_option
from flask import Flask, redirect, render_template, g, flash, session, request, Response
from models import Favorite, db, connect_db, User, Drink
import requests
from forms import SignupForm, LoginForm
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///cap1'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'i will not tell you the secret key'

CURR_USER_KEY = 'curr_user'

connect_db(app)

@app.before_request
def add_user_to_g():
    """If user is logged in, add current user to flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/')
def index():
    """Root page"""

    if g.user:
        user = User.query.get_or_404(g.user.id)
        favs = user.favorites

        return render_template('index.html', favs=favs)
    else:
        return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Render sign up template and handle form submission"""

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username = form.username.data,
                password = form.password.data
            )
            db.session.commit()
        
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('user/signup.html', form=form)

        do_login(user)
        flash("Yay! You signed up!", 'success')
        return redirect('/')

    else: 
        return render_template('user/signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Render form to login a user and handle form submission"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(username=form.username.data, password=form.password.data)
        if user:
            do_login(user)
            flash(f'Hello {user.username}!', 'success')
            return redirect('/')
        else:
            flash('Invalid Credentials :/', 'danger')
            return redirect('/login')

    else: 
        return render_template('user/login.html', form=form)

@app.route('/logout')
def logout():
    """Logout a user."""

    do_logout()
    flash('See ya later!', 'success')
    
    return redirect('/')

def search(term):
    """Search the database based on a term and return query object"""

    q_obj = Drink.query.filter(Drink.name.ilike(f'{term}%'))
    return q_obj

@app.route('/search/')
@app.route('/search/<int:page>')
def handle_search(page=1):
    """Search the cocktails api based on a specific search term"""

    per_page=9
    
    try:
        term = request.args['term']
        session['term'] = term
        drinks = search(term).paginate(page, per_page, error_out=False)

        return render_template('search.html', drinks=drinks)

    except KeyError:
        drinks = search(session['term']).paginate(page, per_page, error_out=False)

        return render_template('search.html', drinks=drinks)

@app.route('/drinks/<int:id>')
def show(id):
    """Show page for a drink"""

    drink = Drink.query.get_or_404(id)

    return render_template('drinks/show.html', drink=drink)

@app.route('/drinks/<int:id>/delete')
def delete(id):
    """Delete a drink from favorites list."""

    fav_to_delete = Favorite.query.filter_by(user_id=g.user.id, drink_id=id).first()
    db.session.delete(fav_to_delete)
    db.session.commit()

    flash('Removed from favorites', 'danger')
    return redirect(f'/users/{g.user.id}/favorites')


@app.route('/users/<int:id>/favorites', methods=['GET'])
def show_favs(id):
    """Show the favorites page for the user with specific id"""

    user = User.query.get_or_404(id)

    favs = user.favorites
    return render_template('user/favorites.html', user=user, favs=favs)

@app.route('/users/<int:drink_id>/favorites', methods=['POST'])
def add_fav(drink_id):
    """Add a drink to the list of favorites for a user"""

    try:

        favorite = Favorite(user_id=g.user.id, drink_id=drink_id)

        db.session.add(favorite)
        db.session.commit()

    except AttributeError:
        flash('Must be logged in to favorite a drink.', 'danger')
        return redirect('/login')


    return redirect(f'/users/{g.user.id}/favorites')