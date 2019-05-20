from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, session, flash, request, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, SpeciesIndividual, Drug, Condition

from calculator import get_instructions

from dose_recommender import filter_dose_using_species

from queries import get_list_of_drugs

import json

from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from werkzeug.security import generate_password_hash, check_password_hash

# Creates an instance of a Flask object
app = Flask(__name__)

# For Flask session - CHANGE THIS LATER!!!
app.config['SECRET_KEY'] = 'key'

# Throws an error if an undefined variable is used in Jinja
app.jinja_env.undefined = StrictUndefined

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # Associates the user id stored in the cookie with the right user object.
    return User.query.get(int(user_id))


@app.route('/')
def index():
    """Renders the homepage"""
    return render_template("homepage.html")

@app.route('/get-drug-names')
def get_drug_names():
    """Returns all the current drugs"""

    drug_dict = get_list_of_drugs()

    drugs = json.dumps(drug_dict)

    return drugs

###!!!! Route for viewing individual drug pages
@app.route('/drug/<drug_id>')
def get_drug_page(drug_id):

    drug = Drug.query.get(drug_id)

    return render_template("drug_page.html",
                           drug=drug)

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

@app.route('/pick-dose')
def pick_dose():
    """Displays info from data base to help user decide on a dose"""

    info = {
        'drugs' : Drug.query.all(),
        'species_groups' : SpeciesIndividual.query.all(),
        'conditions' : Condition.query.all(),
    }

    return render_template("pick_dose.html",
                           info=info)

@app.route('/dosing-info')
def get_dose_info():
    """Returns a form for the user to input the doses they want"""

    species_list = SpeciesIndividual.query.all()


    ##### request.args gets a string, not the actual object. Need to fix this bug.

    drug_id = request.args.get("drug")
    species_id = request.args.get("species")
    condition_id = request.args.get("condition")

    drug = Drug.query.get(drug_id)
    species = SpeciesIndividual.query.get(species_id)
    condition = Condition.query.get(condition_id)

    doses = filter_dose_using_species(drug, species)

    return render_template("input_calculate.html",
                           doses=doses)

@app.route('/calculate-dose')
def calculate_dose():
    """Gets information inputed by user and calls the dose calculator function"""

    weight = float(request.args.get("weight"))
    dose = float(request.args.get("dose"))
    duration = float(request.args.get("duration"))
    frequency = float(request.args.get("frequency"))
    #Concentration refers to concentration of a liquid formula or the strength of a tablet
    concentration = float(request.args.get("concentration"))
    form = request.args.get("form")
    divide = int(request.args.get("divide"))

    instruction_info = get_instructions(weight, dose, concentration, duration, frequency, form, divide)

    return render_template("label_instructions.html",
                           instruction_info=instruction_info)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('No user or incorrect password, please check your login details.')
        return redirect('/login')

    login_user(user, remember=remember)

    return redirect('/profile')

@app.route('/profile')
@login_required
def profile():
    fname = current_user.fname
    lname = current_user.lname

    return render_template('profile.html',
                           fname=fname,
                           lname=lname)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    username = request.form.get('username')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('You already have an account')
        return redirect('/login')

    new_user = User(email=email,
                    fname=fname,
                    lname=lname,
                    username=username,
                    password=generate_password_hash(password, method="pbkdf2:sha256", salt_length=8),
                    user_type='vet')

    db.session.add(new_user)
    db.session.commit()

    flash("Welcome! Thanks for signing up!")

    return redirect('/login')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/add-preferred-dose/<drug_id>')
def save_dose():
    return render_template("add_dose.html")

# @app.route('/add-preferred-dose', methods=["POST"])
# def save_dose_post():
#     pass

if __name__ == "__main__":
    app.debug = True

    # So templates are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use Debug Toolbar extension
    DebugToolbarExtension(app)

    app.run()
