from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from datetime import datetime


db = SQLAlchemy()

#############################
#Logins:
# @login_manager.user_loader
# def get_user(ident):
#   return User.query.get(int(ident))

#############################
# Model definitions

#Followers association table
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
                    db.Column('followed_id', db.Integer, db.ForeignKey('users.id')))

class User(db.Model, UserMixin):
    """Stores information about each user"""

    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_role = db.Column(db.String(10), nullable=False)

    # Relationships
    #.vet to access relationship to vet class
    #.doses - to access the doses created by this user.
    #.forked_doses : References to a list of preferred dose objects.

    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def get_urole(self):
        return self.user_role

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0


    def __repr__(self):
        """Represents a user object"""

        return f"<User Name: {self.fname} {self.lname} Type: {self.user_role}>"



class Vet(db.Model, UserMixin):
    """Stores information about each vet"""

    __tablename__ = "vets"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)
    grad_year = db.Column(db.DateTime, nullable=True)
    specialty = db.Column(db.String(200), nullable=True)

    user = db.relationship("User",
                           backref=db.backref("vet"),
                           uselist=False)


    def __repr__(self):
        """Represent a vet object"""

        return f"<Vet vet_id: {self.id}>"


class Drug(db.Model):
    """Stores information about each drug"""

    __tablename__ = "drugs"

    drug_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    generic_name = db.Column(db.String(100), nullable=False)

    # .doses - to see the list of dose objects for this drug.
    #.forked_doses - refers to the preferred doses for this drug.

    #!!!! For future linking to therapeutic groups
    # therapeutic_groups = db.relationship("TherapeuticGroup",
    #                                      secondary="groups_drugs",
    #                                      backref="drugs")

    def __repr__(self):
        """Represents a drug object"""

        return f"<Drug Name: {self.generic_name}>"

class Form(db.Model):
    """Stores information about the possible drug forms"""

    __tablename__ = "forms"

    form_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    form_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        """Represents a form object"""

        return f"<Form form_name: {self.form_name}>"

class Formulation(db.Model):
    """Stores information about drug strengths & their form"""

    __tablename__ = "formulations"

    strength_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    drug_id = db.Column(db.Integer,
                        db.ForeignKey('drugs.drug_id'))
    drug_form_id = db.Column(db.Integer,
                             db.ForeignKey('forms.form_id'))

    strength = db.Column(db.Float)
    units = db.Column(db.String(5))

    def __repr__(self):
        """Represents a drug strength object"""

        return f"<Strength drug: {self.drug_id}, form: {self.form_id} strength: {self.strength}{self.units} >"

class ForkedDose(db.Model):
    """Stores the preferred doses for each vet"""

    __tablename__ = "forked_doses"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    drug_id = db.Column(db.Integer,
                        db.ForeignKey('drugs.drug_id'))
    user_id = db.Column(db.Integer,
                       db.ForeignKey('users.id'))
    dose_id = db.Column(db.Integer,
                        db.ForeignKey('personal_doses.dose_id'))

    user = db.relationship('User',
                          backref=db.backref("forked_doses"))
    dose = db.relationship('PersonalDose',
                           backref=db.backref("forked_dose"))
    drug = db.relationship('Drug',
                           backref=db.backref("forked_doses"))

    def __repr__(self):
        """Represents a preferred dose object"""

        return f"<ForkedDose forked by {self.user.fname}>"



# class TherapeuticGroup:
#     """Stores the different possible therapeutic groups. eg anti-infective, anaesthetic, analgesic etc."""
#
#     __tablename__ = "therapeutic_groups"
#
#     group_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     therapeutic_group = db.Column(db.String(100), unique=True, nullable=False)
#
#     def __repr__(self):
#         """Represents a therapeutic group object"""
#
#         return f"<TherapeuticGroup: {self.therapeutic_group}>"
#
#
# class GroupDrug:
#     """The association table between therapeutic_groups and drugs."""
#
#     __tablename__ = "groups_drugs"
#
#     group_drug_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     therapeutic_group_id = db.Column(db.Integer,
#                                      db.ForeignKey('therapeutic_groups.group_id'),
#                                      nullable=False)
#     drug_id = db.Column(db.Integer,
#                         db.ForeignKey('drugs.drug_id'),
#                         nullable=False)

    # .drugs - to access the drugs in each therapeutic group

class SpeciesGroup(db.Model):
    """Sets up the table for the species groups"""

    __tablename__ = "species_groups"

    species_group_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    species_group = db.Column(db.String(50), nullable=False)

    # .species_individuals - references the individual species objects of a group.
    # .doses - to see the doses associated with this species group

    def __repr__(self):
        """Represents a Species_group object"""

        return f"<SpeciesGroup species_group:{self.species_group}>"

class SpeciesIndividual(db.Model):
    """Sets up the class for the individual species"""

    __tablename__ = "species_individuals"

    species_individual_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    species_name = db.Column(db.String(50), nullable=False)
    species_group_id = db.Column(db.Integer,
                       db.ForeignKey('species_groups.species_group_id'),
                       nullable=False)

    species_group = db.relationship('SpeciesGroup',
                           backref=db.backref('species_individuals'))

    def __repr__(self):
        """Represent a species individual object"""

        return f"<Species_individual Name: {self.species_name}, Group ID: {self.species_group_id}>"

class Route(db.Model):
    """Sets up the table for the routes"""

    __tablename__ = "routes"

    route_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    route = db.Column(db.String(30), nullable=False)
    route_acronym = db.Column(db.String(30), nullable=True)

    def __repr__(self):
        """Represents a route object"""

        return f"<Route route: {self.route}, route_acronym: {self.route_acronym}>"


class Condition(db.Model):
    """Sets up the diseases table"""

    __tablename__ = "conditions"

    condition_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    condition = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        """Represents a disease object"""

        return f"<Disease: {self.condition}>"

class PersonalDose(db.Model):
    """Sets up table to store doses created by individuals - ie doses not sourced from textbooks"""


    __tablename__ = "personal_doses"

    dose_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    drug_id = db.Column(db.Integer,
                        db.ForeignKey("drugs.drug_id"),
                        nullable=False)
    dose_lower = db.Column(db.Float, nullable=True)
    dose_upper = db.Column(db.Float, nullable=True)
    recommended_dose = db.Column(db.Float, nullable=True)

    species_group_id = db.Column(db.Integer,
                                db.ForeignKey("species_groups.species_group_id"))
    individual_species_id = db.Column(db.Integer,
                                      db.ForeignKey("species_individuals.species_individual_id"))

    condition_id = db.Column(db.Integer,
                             db.ForeignKey("conditions.condition_id"))

    creator_id = db.Column(db.Integer,
                           db.ForeignKey("users.id"))

    duration_days = db.Column(db.Integer, nullable=True)

    frequency_hrs = db.Column(db.String(10), nullable=True)

    #Relationships:

    drug = db.relationship('Drug',
                           backref=db.backref('doses'))

    species_group = db.relationship('SpeciesGroup',
                                    backref=db.backref('doses'))

    individual_species = db.relationship('SpeciesIndividual',
                                        backref=db.backref('doses'))

    condition = db.relationship('Condition',
                                    backref=db.backref('doses'))

    creator = db.relationship('User',
                                    backref=db.backref('doses'))

    #Backrefs:
    # .preferred_dose : refers to the preferred dose instance.

    def __repr__(self):
        """Represents a personal dose object."""

        return f"<PersonalDose drug_id: {self.drug.generic_name}, creator: {self.creator.fname}, species: {self.individual_species.species_name}, group: {self.species_group.species_group} >"


#############################
# Helper functions

def connect_to_db(app):
    """ Connect the database to the Flask app"""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///vetcalc'
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    # If model.py is run interactively,
    # the database can be interacted with directly.

    from server import app
    connect_to_db(app)
    print("Connected to database")


