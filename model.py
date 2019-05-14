from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#############################
# Model definitions

class User(db.Model):
    """Stores information about each user"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String(60), nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        """Represents a user object"""

        return f"<User Name: {self.fname} {self.lname} Type: {self.user_type}"


class Vets(db.Model):
    """Stores information about each vet"""

    vet_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False)
    grad_year = db.Column(db.DateTime, nullable=True)
    specialty = db.Column(db.String(150), nullable=True)



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


