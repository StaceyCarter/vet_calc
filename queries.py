from model import Drug, SpeciesGroup, SpeciesIndividual, Route, Condition, User, PersonalDose, Form, Formulation, ForkedDose
from model import connect_to_db, db

def get_list_of_drugs():
    """Returns a list of all the drug names"""

    drugs = Drug.query.order_by('generic_name').all()

    drug_dict = {}

    for drug in drugs:
        drug_dict[drug.generic_name] = drug.drug_id

    # list_drugs = [drug.generic_name for drug in drugs]

    return drug_dict

def get_user_doses_for_drug(id, drug_id):
    """Queries the database for a particular user id and drug_id to find all the user's preferred doses for a particular drug.

    Returns a list of dictionaries with the information of interest about each dose, namely:
    - lower range
    - upper range
    - recommended dose
    - species it is intended for
    - condition (if any) it is intended for.

    :param id: currently logged in user's id
    :type int:

    :param drug_id: Drug id of interest
    :type int:

    :returns: List of dictionaries containing information of interest about a dose.

    """

    doses = PersonalDose.query.filter((PersonalDose.drug_id == drug_id) & (PersonalDose.creator_id == id)).all()

    info = []

    for dose in doses:
        dose_info = extract_dose_info(dose)

        info.append(dose_info) #list comp

    return info

def extract_dose_info(dose):
    """Takes in a drug dose object and returns the relevant info it contains. Returns a dictionary."""

    dose_info = {}

    if dose.individual_species.species_individual_id == 1:
        dose_info['species'] = dose.species_group.species_group
    else:
        dose_info['species'] = dose.individual_species.species_name

    if dose.condition.condition_id != 1:
        dose_info['condition'] = dose.condition.condition

    if dose.dose_lower:
        dose_info['lower'] = dose.dose_lower
    if dose.dose_upper:
        dose_info['upper'] = dose.dose_upper
    if dose.recommended_dose:
        dose_info['recommended'] = dose.recommended_dose

    dose_info['dose_id'] = dose.dose_id

    return dose_info


def get_user_personal_doses(id):
    """Retrieves all the drugs the user has saved personal doses for."""

    edited_drugs = PersonalDose.query.filter(PersonalDose.creator_id == id).distinct(PersonalDose.drug_id).all()

    users_drugs = {}

    for drug in edited_drugs:
        users_drugs[drug.drug.generic_name] = get_user_doses_for_drug(id, drug.drug_id)

    return users_drugs

def get_forked_dose_for_drug(id, drug_id):
    """Returns a dictionary with all useful dose info about a particular drug."""

    forked_doses = ForkedDose.query.filter((ForkedDose.drug_id == drug_id) & (ForkedDose.user_id == id)).all()

    info = []

    for forked_dose in forked_doses:
       dose = forked_dose.dose
       dose_info = extract_dose_info(dose)
       creator = f"{dose.creator.fname} {dose.creator.lname}"
       dose_info['creator'] = creator

       info.append(dose_info)

    return info


def get_user_forked_doses(user_id):

    # forked_doses = ForkedDose.query.filter_by(user_id=user_id).all()

    forked_drugs = ForkedDose.query.filter(ForkedDose.user_id == user_id).distinct(ForkedDose.drug_id).all()

    forked_drug_info = {}

    for drug in forked_drugs:
        forked_drug_info[drug.drug.generic_name] = get_forked_dose_for_drug(user_id, drug.drug_id)

    return forked_drug_info

def get_vet_grad_and_specialty(user):
    """Takes in a user object and tries to access the grad year"""

    vet_obj = user.vet

    try:
        grad_year = vet_obj.grad_year
    except AttributeError:

        grad_year = None

    try:
        specialty = vet_obj.specialty
    except AttributeError:
        specialty = None

    return {
        'grad_year' : grad_year,
        'specialty' : specialty
    }



if __name__ == "__main__" :
    from server import app

    connect_to_db(app)