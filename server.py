from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, session, flash, request, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, SpeciesIndividual, Drug, Condition, SpeciesGroup, PreferredDose, PersonalDose

from calculator import get_instructions, generate_instructions

from dose_recommender import filter_dose_using_species

from queries import get_list_of_drugs, get_user_doses, get_user_personal_doses

from send_text import send_message

from helpers import upload_file_to_s3

import json

from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.utils import secure_filename


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


@app.route('/drug/<drug_id>')
def get_drug_page(drug_id):
    """View an individual drug page"""

    user = current_user.id

    saved_doses = get_user_doses(user, drug_id)

    drug = Drug.query.get(drug_id)

    return render_template("drug_page.html",
                           drug=drug,
                           saved_doses=saved_doses)

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
    """Gets information input by user and calls the dose calculator function"""

    weight = float(request.args.get("weight"))
    dose = float(request.args.get("dose"))
    duration = float(request.args.get("duration"))
    frequency = float(request.args.get("frequency"))
    #Concentration refers to concentration of a liquid formula or the strength of a tablet
    concentration = float(request.args.get("concentration"))
    form = request.args.get("form")
    divide = int(request.args.get("divide"))

    instruction_info = get_instructions(weight, dose, concentration, duration, frequency, form, divide)

    instructions = generate_instructions(instruction_info)

    return render_template("label_instructions.html",
                           instruction_info=instruction_info,
                           instructions=instructions)

@app.route('/prescribe/<dose_id>')
def prescribe(dose_id):
    """Presents the dose calculator, with fields regarding the dose prefilled."""

    dose = PersonalDose.query.get(dose_id)

    return render_template('prescribe.html',
                           dose=dose)


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

    users_doses = get_user_personal_doses(current_user.id)

    return render_template('profile.html',
                           fname=fname,
                           lname=lname,
                           users_doses = users_doses)

@app.route('/other-users')
def other_users():

    users = User.query.all()

    return render_template("other_users.html",
                           users=users,
                           current=current_user.id)

@app.route('/profile/<user_id>')
def view_other_profile(user_id):

    user = User.query.get(user_id)

    users_doses = get_user_personal_doses(user.id)
    print(users_doses)

    return render_template("other_user.html",
                           user=user,
                           users_doses=users_doses)

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


@app.route('/drug/add-preferred-dose/<drug_id>')
def save_dose(drug_id):

    drug = Drug.query.get(drug_id)

    info = {
        'species_groups': SpeciesIndividual.query.all(),
        'conditions': Condition.query.all(),
        'groups': SpeciesGroup.query.all()
    }

    return render_template("add_dose.html",
                           drug=drug,
                           info=info)

@app.route('/drug/add-preferred-dose/<drug_id>', methods=["POST"])
@login_required
def save_dose_post(drug_id):

    lower=request.form.get('lower')
    upper = request.form.get('upper')
    recommended = request.form.get('recommended')
    species = request.form.get('species')
    species_group = request.form.get('group')
    condition = request.form.get('condition')
    duration = request.form.get('duration')
    frequency = request.form.get('frequency')

    new_dose = PersonalDose(
        drug_id=drug_id,
        dose_lower = lower,
        dose_upper = upper,
        recommended_dose = recommended,
        species_group_id = species_group,
        individual_species_id = species,
        condition_id = condition,
        creator_id = current_user.id,
        duration_days = duration,
        frequency_hrs = frequency
    )

    db.session.add(new_dose)
    db.session.commit()

    flash("Your dose has been added")
    return redirect(f'/drug/{drug_id}')

@app.route('/delete/<dose_id>')
def delete_dose(dose_id):

    dose = PersonalDose.query.get(dose_id)
    drug_id = dose.drug_id

    PersonalDose.query.filter_by(dose_id=dose_id).delete()
    db.session.commit()

    flash("dose has been deleted")
    return redirect(f'/drug/{drug_id}')

@app.route('/text-client/<instructions>')
def text_client(instructions):

    send_message(instructions)

    return redirect("/")

@app.route('/add-pic')
def add_pic():
    return render_template("add_pic.html")

@app.route('/add-pic', methods=["POST"])
def upload_pic():

    if "profile_pic" not in request.files:
        return "Can't find file"

    file = request.files['profile_pic']

    if file.filename == "":
        return "please select a file"
    else:
        file.filename = secure_filename(file.filename)
        output = upload_file_to_s3(file)
        return str(output)



if __name__ == "__main__":
    app.debug = True

    # So templates are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use Debug Toolbar extension
    DebugToolbarExtension(app)

    app.run()
