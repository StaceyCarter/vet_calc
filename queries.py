from model import Drug, SpeciesGroup, SpeciesIndividual, Route, Condition, User, PersonalDose, Form, Formulation
from model import connect_to_db, db

def get_list_of_drugs():
    """Returns a list of all the drug names"""

    drugs = Drug.query.order_by('generic_name').all()

    list_drugs = [drug.generic_name for drug in drugs]

    return list_drugs


if __name__ == "__main__" :
    from server import app

    connect_to_db(app)