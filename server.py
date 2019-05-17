from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, SpeciesIndividual, Drug, Condition

from calculator import get_instructions

from dose_recommender import filter_dose_using_species

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

@app.route('/save-dose')
def save_dose():
    return redirect('/')

if __name__ == "__main__":
    app.debug = True

    # So templates are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use Debug Toolbar extension
    DebugToolbarExtension(app)

    app.run()
