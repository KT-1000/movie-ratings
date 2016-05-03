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

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/login')
def sign_in():
    """The user sign-in page."""

    return render_template("sign_in.html")

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
        # redirect to homepage
        return redirect('/')
    # if email and password not db
    else:
        #flash message that username and email don't exist
        flash('Email or password not found')
        # redirect to login page
        return redirect('/login')



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
