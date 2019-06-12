#organize by who wrote these

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, session, flash, request, send_from_directory, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, SpeciesIndividual, Drug, Condition, SpeciesGroup, ForkedDose, PersonalDose, Conversation, Message

from calculator import get_instructions, generate_instructions, get_amount_ml_per_dose

from dose_recommender import filter_dose_using_species

from queries import get_list_of_drugs, get_user_doses_for_drug, get_user_personal_doses, get_user_forked_doses, get_vet_grad_and_specialty

from send_text import send_text_func

from helpers import upload_file_to_s3

from functools import wraps

import json

import boto3

import os

from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.utils import secure_filename

from flask_socketio import SocketIO, Namespace, join_room, leave_room, send, emit, rooms

from PIL import Image

import io

import random

# from pprint import pprint as print


# Creates an instance of a Flask object
app = Flask(__name__)
socketio = SocketIO(app)

# For Flask session - CHANGE THIS LATER!!!
app.config['SECRET_KEY'] = 'key'

# Throws an error if an undefined variable is used in Jinja
app.jinja_env.undefined = StrictUndefined

login_manager = LoginManager()
login_manager.init_app(app)

s3 = boto3.client('s3')

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


@app.route('/<path:path>')
def send_image(path):
    return send_from_directory('static', path)


@app.route('/')

def index():
    """Renders the homepage"""

    if current_user.is_authenticated:
        return render_template("homepage.html")

    if current_user.is_anonymous:
        return render_template("join_vetcalc.html")


@app.route('/get-drug-names')
def get_drug_names():
    """Returns all the current drugs"""

    drug_dict = get_list_of_drugs()

    drugs = json.dumps(drug_dict) #change to jsonify

    return drugs


@app.route('/drug/<drug_id>')
@login_required()
def get_drug_page(drug_id):
    """View an individual drug page"""

    low = random.randint(1,10)
    high = random.randint(15, 25)

    fake_textbook_data = {
        'low' : low,
        'high' : high,
        'recommended' : random.randint(low, high),
        'contraindications' : random.sample(
            ['Gestating', 'Boxers', 'Hypovolaemia', 'Hypotension', 'Dehydration', 'Renal disease'], random.randint(1, 6)),
        'interactions' : random.sample(
            ['NSAIDs', 'Corticosteroids', 'Aminoglycosides', 'Selective serotonin reuptake inhibitors'], random.randint(1, 3)),
        'duration' : random.choice([3, 5, 7, 14, 20, 30]),
        'frequency' : random.choice([12, 24, 8, 48])
    }

    user = current_user.id

    saved_doses = get_user_doses_for_drug(user, drug_id)

    drug = Drug.query.get(drug_id)

    info = {
        'species_groups': SpeciesIndividual.query.all(),
        'conditions': Condition.query.all(),
        'groups': SpeciesGroup.query.all()
    }

    return render_template("drug_page.html",
                           drug=drug,
                           saved_doses=saved_doses,
                           textbook = fake_textbook_data,
                           info = info)


@app.route('/register')
def register_user():
    """Returns register form to become a user"""

    return render_template("add_user.html")

@app.route('/pick-dose')
@login_required()
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
@login_required()
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
@login_required()
def calculate_dose():
    """Gets information input by user and calls the dose calculator function"""

    weight = float(request.args.get("weight"))
    dose = float(request.args.get("dose"))
    duration = float(request.args.get("duration"))
    frequency = float(request.args.get("frequency"))
    #Concentration refers to concentration of a liquid formula or the strength of a tablet
    concentration = float(request.args.get("concentration"))
    form = request.args.get("form")
    divide = int(request.args.get("divide") or 1)

    instruction_info = get_instructions(weight, dose, concentration, duration, frequency, form, divide)

    instructions = generate_instructions(instruction_info)

    return render_template("label_instructions.html",
                           instruction_info=instruction_info,
                           instructions=instructions)

@app.route('/prescribe/<dose_id>')
@login_required()
def prescribe(dose_id):
    """Presents the dose calculator, with fields regarding the dose prefilled."""

    dose = PersonalDose.query.get(dose_id)
    print(dose)

    return render_template('prescribe.html',
                           dose=dose)

@app.route('/prescribe-fake-data/<recommended>/<low>/<high>/<frequency>/<duration>/<generic_name>')
@login_required()
def prescribe_from_fake_data(recommended, low, high, frequency, duration, generic_name):
    """ Generates the normal prescribe.html, but from randomly generated fake textbook data"""

    dose = {
        'drug' : {'generic_name' : generic_name},
        'recommended_dose' : recommended,
        'dose_lower' : low,
        'dose_upper' : high,
        'frequency_hrs' : frequency,
        'duration_days' : duration
    }

    return render_template('prescribe.html',
                           dose=dose)

@app.route('/get-amount-ml.json/<concentration>/<dose>/<weight>')
@login_required()
def get_amount_ml(concentration, dose, weight):

    doseF = float(dose)
    weightF = float(weight)
    concentrationF = float(concentration)

    amount = get_amount_ml_per_dose(doseF, concentrationF, weightF)

    data = {
        'amount' : amount
    }

    return jsonify(data)



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

    user = current_user
    following = len(user.followed.all())
    followers = len(user.followers.all())

    grad_spec = get_vet_grad_and_specialty(user)

    if user.user_role == "vet":
        specialty = current_user

    users_doses = get_user_personal_doses(current_user.id)
    forked_doses = get_user_forked_doses(current_user.id)

    if current_user.pic:
        image = current_user.pic
    else:
        image = 'vetcalc_profilepic.jpg'


    url = s3.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': os.environ.get('S3_BUCKET'),
                                    'Key': image,
                                },
                                ExpiresIn=3600)

    drugs = [drug.lower() for drug in users_doses]

    for drug in forked_doses:
        drugs.append(drug.lower())

    drugs = list(set(drugs))

    return render_template('profile.html',
                           fname=fname,
                           lname=lname,
                           users_doses = users_doses,
                           forked_doses = forked_doses,
                           url = url,
                           user = user,
                           grad_spec = grad_spec,
                           following = following,
                           followers = followers,
                           drugs = drugs)


@app.route('/get-profile-pic-thumb.json')
def get_profile_pic_thumbnail():
    """Generates presigned url for the current user's profile picture"""

    if current_user.pic:
        image = current_user.pic + 'thumbnail'
    else:
        image = 'vetcalc_profilepicthumbnail.jpg'


    url = s3.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': os.environ.get('S3_BUCKET'),
                                    'Key': image,
                                },
                                ExpiresIn=3600)

    return jsonify(url)

@app.route('/get-profile-pic-thumb-other/<user_id>')
def get_profile_pic_thumbnail_other_user(user_id):
    """Gets thumbnail of a user's profile pic given a user id"""
    pass


@app.route('/other-users')
@login_required()
def other_users():

    users = User.query.all()

    users_info = [[user.username, user.fname, user.lname] for user in users]

    return render_template("other_users.html",
                           users=users,
                           current=current_user.id,
                           users_info=users_info)

@app.route('/profile/<user_id>')
@login_required()
def view_other_profile(user_id):

    user = User.query.get(user_id)

    following = len(user.followed.all())
    followers = len(user.followers.all())

    is_following = current_user.is_following(user)

    users_doses = get_user_personal_doses(user.id)
    print(users_doses)

    if user.pic:
        image = user.pic
    else:
        image = 'vetcalc_profilepic.jpg'


    url = s3.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': os.environ.get('S3_BUCKET'),
                                    'Key': image,
                                },
                                ExpiresIn=3600)

    drugs = [drug.lower() for drug in users_doses]


    return render_template("other_user.html",
                           user=user,
                           users_doses=users_doses,
                           url=url,
                           following=following,
                           followers=followers,
                           drugs=drugs,
                           is_following=is_following)

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
                    password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8),
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

@app.route('/drug/add-preferred-dose/<drug_id>', methods=['POST'])
@login_required()
def save_dose_post(drug_id):

    lower=request.form.get('lower') or None
    upper = request.form.get('upper') or None
    recommended = request.form.get('recommended') or None
    species = request.form.get('species') or None
    species_group = request.form.get('group') or None
    condition = request.form.get('condition')
    duration = request.form.get('duration') or None
    frequency = request.form.get('frequency') or None

    new_dose = PersonalDose(
        drug_id=drug_id,
        dose_lower = lower,
        dose_upper = upper,
        recommended_dose = recommended,
        species_group_id = species_group,
        individual_species_id = species,
        condition_id = 1,
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
@login_required()
def delete_dose(dose_id):

    dose = PersonalDose.query.get(dose_id)
    drug_id = dose.drug_id

    PersonalDose.query.filter_by(dose_id=dose_id).delete()
    db.session.commit()

    flash("dose has been deleted")
    return redirect(f'/drug/{drug_id}')

@app.route('/text-client.json', methods=['POST'])
@login_required()
def text_client():

    data = request.get_json()

    phone = '+1' + data['phone']
    instructions = data['instructions']

    send_text_func(instructions, phone)

    return redirect("/") #FIX

@app.route('/add-pic')
@login_required()
def add_pic():
    return render_template("add_pic.html")

@app.route('/add-pic', methods=['POST'])
@login_required()
def upload_pic():

    s3 = boto3.resource('s3')

    pic_from_user = request.files['profile_pic']


    image = Image.open(pic_from_user)
    imageThumb = image.copy()

    image.thumbnail([200, 200])
    imageThumb.thumbnail([50, 50])

    in_mem_file = io.BytesIO()

    image.save(in_mem_file, format='JPEG', quality=95)

    file = in_mem_file.getvalue()

    imageThumb.save(in_mem_file, format='JPEG', quality=95)

    fileThumb = in_mem_file.getvalue()

    # Rename file for unique storage
    user = User.query.get(current_user.id)
    #Checks if user has already uploaded and increments the count of their pic by one so it doesn't clash with pictures already stored in the bucket.
    if user.pic:
        link = user.pic.split('_')
        num = int(link[-1])
        filename = f'{current_user.email}_profilepic_{num + 1}'
    else:
        filename = f'{current_user.email}_profilepic_1'

    user.pic = filename
    db.session.commit()


    s3.Bucket(os.environ.get('S3_BUCKET')).put_object(Key=filename, Body=file)
    s3.Bucket(os.environ.get('S3_BUCKET')).put_object(Key=filename + 'thumbnail', Body=fileThumb)

    return redirect('/profile')


#### SHOULD BE A POST METHOD!!!
@app.route('/fork/<dose_id>')
@login_required()
def fork_dose(dose_id):

    dose = PersonalDose.query.get(dose_id)



    fork = ForkedDose(drug_id=dose.drug_id,
                      user_id=current_user.id,
                      dose_id=dose_id)

    db.session.add(fork)
    db.session.commit()

    flash("Saved to your doses")

    return redirect(f'/profile/{dose.creator.id}')

@app.route('/follow/<user_id>', methods=['POST'])
@login_required()
def follow(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user == None:
        return jsonify("User not found")
    if user == current_user:
        return jsonify("You can't follow yourself")

    current_user.follow(user)
    db.session.commit()

    return jsonify("You have followed")



@app.route('/unfollow/<user_id>', methods=['POST'])
@login_required()
def unfollow(user_id):

    user = User.query.filter_by(id=user_id).first()

    if user == None:
        return jsonify("user not found")

    current_user.unfollow(user)
    db.session.commit()

    return jsonify("You have unfollowed")

@app.route('/profile/following/<user_id>')
@login_required()
def see_following(user_id):

    user = User.query.get(user_id)

    following = user.followed.all()

    return render_template("following.html",
                           following = following,
                           user = user)

@app.route('/profile/followers/<user_id>')
@login_required()
def see_followers(user_id):

    user = User.query.get(user_id)

    followers = user.followers.all()

    return render_template("followers.html",
                           followers = followers,
                           user = user)

@app.route('/profile/chat/<user_id>')
@login_required()
def check_or_create_conversation(user_id):
    """Checks if there is a chat history between the current user and the other user_id. If there is, it loads the history,
    if there isn't it creates a row in the table. Users are assigned to messager1 or 2 depending on whose user is is larger.

    """

    bigger = max(current_user.id, int(user_id))
    lower = min(current_user.id, int(user_id))
    conversation = Conversation.query.filter((Conversation.messager_1 == bigger) & (Conversation.messager_2 == lower)).first()

    if not conversation:
        new_convo = Conversation(messager_1=bigger,
                     messager_2=lower)

        db.session.add(new_convo)
        db.session.commit()

        # As soon as the conversation has been added to the database, query the database for the conversation.
        conversation = Conversation.query.filter((Conversation.messager_1 == bigger) & (Conversation.messager_2 == lower)).first()

    return redirect(f'/chat/messages/{conversation.id}')


@app.route('/chat/messages/<conversation_id>')
@login_required()
def chat(conversation_id):

    fname = current_user.fname
    lname = current_user.lname

    convo = Conversation.query.get(conversation_id)

    if convo.messager_1 != current_user.id:
        other_user = convo.messager_1
    else:
        other_user = convo.messager_2

    # Collects all previous messages with this conversation id and orders them by timestamp
    previous_messages = Message.query.order_by(Message.timestamp.desc()).filter(Message.conversation_id == conversation_id).paginate(page=1, per_page=10, error_out=False)

    # Sets all unseen messages to seen on page load.
    unseen_messages = Message.query.filter((Message.conversation_id == conversation_id) & (Message.seen == False)).all()

    for message in unseen_messages:
        message.seen = True

    db.session.commit()

    return render_template('chat.html',
                           name = f'{fname} {lname}',
                           previous_messages= reversed(previous_messages.items),
                           other_user = other_user)

@app.route('/chat/messages/<conversation_id>/<page>.json')
@login_required()
def load_more_messages(conversation_id, page):
    """Infinite scroll function """

    pageInt = int(page)

    previous_messages = Message.query.order_by(Message.timestamp.desc()).filter(
        Message.conversation_id == conversation_id).paginate(page=pageInt, per_page=10, error_out=False)


    message_json = {
        'currentUser' : str(current_user.id),
        'username' : str(current_user.username)
    }

    i = 0
    for message in previous_messages.items:
        key = str(i)
        username = message.sender_user.username
        message_json[key] = [message.sender, username, message.message_body]
        i += 1

    return jsonify(message_json)

@app.route('/conversations')
@login_required()
def list_conversations():

    conversations = Conversation.query.filter((Conversation.messager_1 == current_user.id) | (Conversation.messager_2 == current_user.id)).all()

    # For each of the conversations the user is involved in, check the messages to see if there are any unseen in the database where the
    # current user is not the sender.

    convo_with_seen = []

    for conversation in conversations:
        tally = 0
        messages = conversation.messages
        for message in messages:
            if message.seen == False and message.sender != current_user.id:
                tally += 1
        convo_with_seen.append((conversation, tally))

    return render_template('conversations.html',
                           convo_with_seen=convo_with_seen,
                           current=current_user.id)


@socketio.on('join')
def on_join(data):
    username = current_user.username
    room = data['room']

    join_room(room)
    emit('my_response', {'data' : username + ' has entered the room.'}, room=room)

@socketio.on('message')
def send_message(data):
    """Receives a message entered by a client in a chat room. Saves the message to the data base and then re-emits the
    message to the rest of the chat room with the username set to whoever is logged in.

    """


    new_message = Message(
        conversation_id = data['room'],
        message_body = data['message'],
        sender = current_user.id,
    )
    db.session.add(new_message)
    db.session.commit()

    message_id = db.session.query(db.func.max(Message.id)).first()

    room = data['room']

    # Sets the username to be the person who is logged in.
    data['username'] = current_user.username
    data['sender'] = current_user.id
    data['messageID'] = message_id

    emit('my_response', data, room=room)

@socketio.on('leave')
def on_leave(data):
    username = current_user.username
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)

@app.route('/chat/messages/markread.json', methods=['POST'])
def mark_as_read():
    """Marks messages as read when a user is logged into chat"""
    data = request.get_json()

    try:
        message = data['messageID'][0]
    except KeyError:
        message = None

    print("\n\n\n\n\n I HAVE RECIEVED THIS JSON: ", message)

    if message:

        m = Message.query.get(int(message))
        m.seen = True

        db.session.commit()

    return "success"









if __name__ == "__main__":
    app.debug = True

    # So templates are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use Debug Toolbar extension
    DebugToolbarExtension(app)

    # app.run()
    socketio.run(app)