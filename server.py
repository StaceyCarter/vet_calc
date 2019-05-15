from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User

# Creates an instance of a Flask object
app = Flask(__name__)

# For Flask session - CHANGE THIS LATER!!!
app.config['SECRET_KEY'] = 'key'

# Throws an error if an undefined variable is used in Jinja
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Renders the homepage"""
    return render_template("homepage.html")

@app.route('/adduser', methods=["POST"])
def add_user():
    """Renders a form to add a user to the database"""

    email = request.form.get('email')
    password = request.form.get('password')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    username = request.form.get('username')


    grad_year = request.form.get('gradYear')
    speciality = request.form.get('specialty')
    user_type = "vet"


    user = User(email = email,
                password = password,
                fname = fname,
                lname = lname,
                username = username,
                user_type = user_type
                )

    db.session.add(user)
    db.session.commit()

    flash("Welcome to the database!")

    return redirect('/')

@app.route('/register')
def register_user():
    """Returns register form to become a user"""

    return render_template("add_user.html")



if __name__ == "__main__":
    app.debug = True

    # So templates are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use Debug Toolbar extension
    DebugToolbarExtension(app)

    app.run()
