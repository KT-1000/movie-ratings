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

    # this returns a movie object 
    movie = (db.session.query(Movie).filter(Movie.movie_id==movie_id).one())

    current_user_id = session.get('user_id')
    # will update if there is a user rating, or will be passed to Jinja if None
    current_user_rating = None

    # If user is logged in 
    if current_user_id:
        # check to see if user has rated the movie
        # current_user_rating = (rating_id, movie_id, user_id, score)
        current_user_rating = (db.session.query(Rating)
        .filter(Rating.user_id == current_user_id, Rating.movie_id == movie_id).first())
    # If user isn't logged in, redirect to login page
    # else:
    #     flash("Please log in to rate a movie.")

    movie_ratings = (db.session.query(Rating.score, Rating.user_id).filter(Rating.movie_id==movie_id).all())

    return render_template("movie_details.html", movie=movie, movie_ratings=movie_ratings, 
        current_user_id=current_user_id, current_user_rating=current_user_rating)

@app.route('/rate_movie', methods=["POST"])
def rate_movie():
    """Updates current rating or adds a new rating."""

    # if user is in session 
    current_user_id = session.get('user_id')

    user_id = request.form.get("user_id")
    movie_id = request.form.get("movie_id")
    score = request.form.get("score")

    if current_user_id:
        # check db to see if there is a row with the user id and score
        current_user_rating = (db.session.query(Rating)
            .filter(Rating.user_id == user_id, Rating.movie_id == movie_id).first())
        # Holds true if the user has rated the movie
        if current_user_rating:
            # update the existing rating object
            current_user_rating.score = score
        else:
            # movie_id = int(movie_id)
            new_rating = Rating(movie_id=movie_id, score=score, user_id=user_id)
            db.session.add(new_rating)

        db.session.commit()
        
    # else flash message to please log in
    else:
        flash('Please log in to rate a movie.')

    return redirect('/movies/' + movie_id)

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



@app.route('/login', methods=["GET"])
def login():
    """The user login page."""

    return render_template("login.html")

# TO DO FIX ME 
@app.route('/registration', methods=["POST"])
def add_user():
    """Adds a new user to the db and logs them in"""

    # retrieves new user information from new_user form
    email = request.form.get("email")
    password = request.form.get("password")
    zipcode = request.form.get("zipcode")
    age = int(request.form.get("age"))
    
    # check if the email retrieved is in the db already 
    # query the db for the email
    user_id = db.session.query(User.user_id).filter(User.email == email).first()
    if user_id:
        flash('That email is already in use!')

        return redirect('/registration')
    else:
        # creates a new_user record when they aren't in the database
        new_user = User(email=email, password=password, zipcode=zipcode, age=age)
        db.session.add(new_user)
        db.session.commit()

        user_id = db.session.query(User.user_id).filter(User.email == email).first()

        # gets the new user id and adds it to the session       
        session["user_id"] = user_id
        return redirect('/')

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
