from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, session, flash, request, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, SpeciesIndividual, Drug, Condition, SpeciesGroup, ForkedDose, PersonalDose, Conversation

from calculator import get_instructions, generate_instructions

from dose_recommender import filter_dose_using_species

from queries import get_list_of_drugs, get_user_doses_for_drug, get_user_personal_doses, get_user_forked_doses

from send_text import send_message

from helpers import upload_file_to_s3

from functools import wraps

import json

import boto3

import os

from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.utils import secure_filename

from flask_socketio import SocketIO


# Creates an instance of a Flask object
app = Flask(__name__)
socketio = SocketIO(app)

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

def login_required(role="user"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):

            if not current_user.is_authenticated:
                return app.login_manager.unauthorized()
            urole = current_user.get_urole()
            if ((urole != role) and (role != "user")):
                return app.login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper





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

    saved_doses = get_user_doses_for_drug(user, drug_id)

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
@login_required()
def profile():
    fname = current_user.fname
    lname = current_user.lname

    users_doses = get_user_personal_doses(current_user.id)
    forked_doses = get_user_forked_doses(current_user.id)

    s3 = boto3.client('s3')

    if current_user.pic:
        image = current_user.pic
    else:
        image = 'file_name' #### REPLACE THIS WITH A DEFAULT PICTURE



    url = s3.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': os.environ.get('S3_BUCKET'),
                                    'Key': image,
                                },
                                ExpiresIn=3600)


    return render_template('profile.html',
                           fname=fname,
                           lname=lname,
                           users_doses = users_doses,
                           forked_doses = forked_doses,
                           url = url)

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
    user_role = request.form.get('user_role')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('You already have an account')
        return redirect('/login')

    new_user = User(email=email,
                    fname=fname,
                    lname=lname,
                    username=username,
                    password=generate_password_hash(password, method="pbkdf2:sha256", salt_length=8),
                    user_role=user_role)

    db.session.add(new_user)
    db.session.commit()

    flash("Welcome! Thanks for signing up!")

    return redirect('/login')


@app.route('/logout')
@login_required()
def logout():
    logout_user()
    return redirect('/')


@app.route('/drug/add-preferred-dose/<drug_id>')
@login_required('vet')
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
@login_required()
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


#### SHOUDL BE A POST METHOD!!!!!
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

    s3 = boto3.resource('s3')

    file = request.files['profile_pic']

    # Rename file for unique storage
    user = User.query.get(current_user.id)
    #Checks if user has already uploaded and increments the count of their pic by one so it doesn't clash with pictures already stored in the bucket.
    if user.pic:
        link = user.pic.split('_')
        num = int(link[-1])
        file.filename = f'{current_user.email}_profilepic_{num + 1}'
    else:
        file.filename = f'{current_user.email}_profilepic_1'

    user.pic = file.filename
    db.session.commit()

    s3.Bucket(os.environ.get('S3_BUCKET')).put_object(Key=file.filename, Body=file)
    # if "profile_pic" not in request.files:
    #     return "Can't find file"
    #
    # file = request.files['profile_pic']
    #
    # if file.filename == "":
    #     return "please select a file"
    # else:
    #     file.filename = secure_filename(file.filename)
    #     output = upload_file_to_s3(file)
    #     return str(output)
    return redirect('/profile')


#### SHOULD BE A POST METHOD!!!
@app.route('/fork/<dose_id>')
def fork_dose(dose_id):

    dose = PersonalDose.query.get(dose_id)

    fork = ForkedDose(drug_id=dose.drug_id,
                      user_id=current_user.id,
                      dose_id=dose_id)

    db.session.add(fork)
    db.session.commit()

    return redirect('/profile')

@app.route('/follow/<user_id>', methods=["POST"])
@login_required()
def follow(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user == None:
        flash('User not found')
        return redirect("/")
    if user == current_user:
        flash("You can't follow yourself")
        return redirect('/profile')

    current_user.follow(user)
    db.session.commit()

    flash(f"You're now following {user.fname}")

    return redirect(f"/profile/{user_id}")

@app.route('/unfollow/<user_id>', methods=["POST"])
@login_required()
def unfollow(user_id):

    user = User.query.filter_by(id=user_id).first()

    if user == None:
        flash('User not found')
        return redirect("/")

    current_user.unfollow(user)
    db.session.commit()

    flash(f"You unfollowed {user.fname}")

    return redirect(f"/profile/{user_id}")

@app.route('/profile/following/<user_id>')
def see_followers(user_id):

    user = User.query.get(user_id)

    following = user.followed.all()

    return render_template("following.html",
                           following = following,
                           user = user)

@app.route('/profile/followers/<user_id>')
def see_following(user_id):

    user = User.query.get(user_id)

    followers = user.followers.all()

    return render_template("followers.html",
                           followers = followers,
                           user = user)

@app.route('/profile/chat/<user_id>')
def check_or_create_conversation(user_id):
    """Checks if there is a chat history between the current user and the other user_id. If there is, it loads the history,
    if there isn't it creates a row in the table. Users are assigned to messager1 or 2 depending on whose user is is larger.

    """

    bigger = max(current_user.id, int(user_id))
    lower = min(current_user.id, int(user_id))
    conversation = Conversation.query.filter((Conversation.messager_1 == bigger) & (Conversation.messager_2 == lower)).first()

    print("\n\n\n\n CONVERSATION: ", conversation)

    if conversation:
        print("\n\n\n\n\n CONVO ALREADY HAPPENING!!!!!")
        return redirect(f'/profile/{user_id}')

    else:
        new_convo = Conversation(messager_1=bigger,
                     messager_2=lower)

        db.session.add(new_convo)
        db.session.commit()
        print(" \n\n\n\n\n COMMITTED ")
        return redirect(f'/')


@app.route('/chat')
def chat():

    fname = current_user.fname
    lname = current_user.lname


    return render_template('chat.html',
                           name = f'{fname} {lname}')

def messageReceived(methods=['GET', 'POST']):
    print('message received!')

@socketio.on('my_event')
def handle_custom_event(json, methods=['GET', 'POST']):
    print('received event: ', str(json))
    socketio.emit('my_response', json, callback=messageReceived)



if __name__ == "__main__":
    app.debug = True

    # So templates are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use Debug Toolbar extension
    DebugToolbarExtension(app)

    app.run()
