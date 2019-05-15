from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension

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

@app.route('/adduser')
def add_user():
    """Renders a form to add a user to the database"""

    

    return render_template("add_user.html")

@app.route('/register', methods=["POST"])
def register_user():
    """Adds a user to the database"""

    ### ADD TO DATABASE

    flash("Welcome to the database!")

    return redirect('/')

if __name__ == "__main__":
    app.debug = True

    # So templates are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    # Use Debug Toolbar extension
    DebugToolbarExtension(app)

    app.run()
