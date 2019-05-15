from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#############################
# Model definitions

class User(db.Model):
    """Stores information about each user"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        """Represents a user object"""

        return f"<User Name: {self.fname} {self.lname} Type: {self.user_type}>"

    #.vet to access relationship to vet class

class Vet(db.Model):
    """Stores information about each vet"""

    __tablename__ = "vets"

    vet_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False)
    grad_year = db.Column(db.DateTime, nullable=True)
    specialty = db.Column(db.String(150), nullable=True)

    user = db.relationship("User",
                           backref=db.backref("vet"))

    def __repr__(self):
        """Represent a vet object"""

        return f"<Vet vet_id: {self.vet_id}>"

class Drug(db.Model):
    """Stores information about each drug"""

    __tablename__ = "drugs"

    drug_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    generic_name = db.Column(db.String(100), nullable=False)
    interactions = db.Column(db.String(), nullable=True)
    contraindications = db.Column(db.String(), nullable=True)

    def __repr__(self):
        """Represents a drug object"""

        return f"<Drug Name: {self.generic_name}>"


class Species_group(db.Model):

    __tablename__ = "species_groups"

    species_group_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    species_group = db.Column(db.String(50), nullable=False)

    # .species_individuals references the individual species objects of a group.

    def __repr__(self):
        """Represents a Species_group object"""

        return f"<Species_group species_group:{self.species_group}>"

class Species_individual(db.Model):

    __tablename__ = "species_individuals"

    species_individual_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    species_name = db.Column(db.String(50), nullable=False)
    species_group_id = db.Column(db.Integer,
                       db.ForeignKey('species_groups.species_group_id'),
                       nullable=False)

    species_group = db.relationship("Species_group",
                           backref=db.backref("species_individuals"))

    def __repr__(self):
        """Represent a species individual object"""

        return f"<Species_individual Name: {self.species_name}, Group ID: {self.species_group_id}>"






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


