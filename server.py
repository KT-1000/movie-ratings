"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/movies')
def movie_list():
    """Shows list of movies"""

    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies)

@app.route('/movies/<int:movie_id>')
def movie_details(movie_id):
    """Retrieving details of a single movie."""

    title, release_date, imdb_url = (db.session.query(Movie.title, Movie.release_date, Movie.imdb_url)
        .filter(Movie.movie_id==movie_id).one())

    movie_ratings = (db.session.query(Rating.score, Rating.user_id).filter(Rating.movie_id==movie_id).all())

    return render_template("movie_details.html", 
                            title=title, 
                            release_date=release_date, 
                            imdb_url=imdb_url, 
                            movie_ratings=movie_ratings)

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<int:user_id>')
def user_details(user_id):
    """Retrieving details of a single user."""

    user_age, user_zipcode = (db.session.query(User.age, User.zipcode)
        .filter(User.user_id==user_id).one())
    # get list of tuples of ratings and movie titles
    user_ratings = (db.session.query(Rating.score, Movie.title)
        .join(Movie).filter(Rating.user_id==user_id).all())
    return render_template("user_details.html", ratings=user_ratings, age=user_age, zipcode=user_zipcode)

@app.route('/login')
def login():
    """The user login page."""

    return render_template("login.html")

@app.route('/validation', methods=["POST"])
def validate_user():
    """Checks to see if user exists in the database and routes appropriately."""
    # get email and password from user submitting form
    user_email = request.form.get("email")
    user_pw = request.form.get("password")
    # query the db to see if user has email and password
    user = User.query.filter(User.email==user_email, User.password==user_pw).first()
    # if email and password exist
    if user:
        # start session based on user id
        session["user_id"] = user.user_id
        flash('You are now logged in')
        # redirect to homepage
        return redirect('/')
    # if email and password not db
    else:
        #flash message that username and email don't exist
        flash('Email or password not found')
        # redirect to login page
        return redirect('/login')

@app.route('/logout')
def logout_user():
    """Logs out the user and removes the session."""

    del session["user_id"]
    flash("You are logged out.")
    return redirect("/")

@app.route('/register')
def register():
    """The new user registration page."""

    return render_template("new_user.html")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
