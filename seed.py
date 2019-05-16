"""Utility file to seed ratings database from seed files"""


from sqlalchemy import func
from model import Drug, SpeciesGroup, SpeciesIndividual, Route, Condition, User, PersonalDose
import datetime
from model import connect_to_db, db
from server import app

def load_users():
    """Seed user data from seed_users.psv

    File format:
    username|fname|lname|email|password|user_type
    """

    print("users")

    User.query.delete()

    with open("seed_data/seed_users.psv") as users:
        for row in users:
            username, fname, lname, email, password, user_type = row.strip().split("|")

            user = User(username=username,
                        fname=fname,
                        lname=lname,
                        email=email,
                        password=password,
                        user_type=user_type)

            db.session.add(user)

        db.session.commit()



def load_drugs():
    """Seed data from drug_seed.psv into the drugs table of the database

    File format:
    Drug name | interactions | contraindications

    """

    print("Drugs")

    Drug.query.delete()

    with open("seed_data/drug_seed.psv") as drugs:
        for row in drugs:
            name = row.strip()

            drug = Drug(generic_name=name)

            db.session.add(drug)

        db.session.commit()

def load_species_groups():
    """Seed data from species_group_seed, each species group has an id associated with it.

    File format:

    group_id | group name

    """

    print("Species groups")

    SpeciesGroup.query.delete()

    with open("seed_data/species_group_seed.psv") as species:
        for row in species:
            species_group_id, species_group_name = row.strip().split("|")

            group = SpeciesGroup(species_group_id = species_group_id,
                         species_group = species_group_name)

            db.session.add(group)

        db.session.commit()


def load_individual_species():
    """Seed data from species_seed, each species is associated with a species group.

    File format:
    species | group_id
    """

    print ("individual species")

    SpeciesIndividual.query.delete()

    with open("seed_data/species_seed.psv") as species:
        for row in species:
            species_name, group_id = row.strip().split("|")

            species = SpeciesIndividual(species_name=species_name,
                                        species_group_id=group_id)

            db.session.add(species)

        db.session.commit()


def load_routes():
    """Seed data from routes_seed.psv into the seed table

    File format:
    route|route_acronym
    """

    print ("routes")

    Route.query.delete()

    with open("seed_data/routes_seed.psv") as routes:
        for row in routes:
            route, route_acronym = row.strip().split("|")

            # Checks if seed is empty, if so, inserts a Null cell into the db
            acronym = None if route_acronym == 'None' else route_acronym

            route = Route(route=route,
                          route_acronym=acronym)


            db.session.add(route)

        db.session.commit()

def load_conditions():
    """Seed data from routes_seed.psv into the seed table

    File format:
    disease
    """

    print ("conditions")

    Condition.query.delete()

    with open("seed_data/disease_seed.psv") as diseases:
        for row in diseases:
            condition = row.strip()

            condition = Condition(condition=condition)

            db.session.add(condition)

        db.session.commit()

def load_personal_doses():
    """Seed data from routes_seed.psv into the seed table

    File format:

    drugname | drug_id | dose_lower | dose_upper | recommended_dose | species_group_id | species_individual_id|
    .... condition_id | creator_id | duration_days | frequency_hrs
    """

    print ("Personal doses")

    PersonalDose.query.delete()

    with open("seed_data/personal_doses_seed.csv") as doses:
        for row in doses:

            dirty_info = row.strip().split(',')

            info = []

            for val in dirty_info:
                if val == 'None' or val == 'none':
                    info.append(None)
                else:
                    info.append(val)


            dose = PersonalDose(
                drug_id = info[1],
                dose_lower = info[2],
                dose_upper = info[3],
                recommended_dose = info[4],
                species_group_id = info[5],
                individual_species_id = info[6],
                condition_id = info[7],
                creator_id = info[8],
                duration_days = info[9],
                frequency_hrs = info[10]
            )

            db.session.add(dose)

        db.session.commit()


def set_val_species_group_id():
    """Set value for the next species_group_id after seeding database"""

    # Get the Max species_group_id in the database
    result = db.session.query(func.max(SpeciesGroup.species_group_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('species_groups_species_group_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Run functions in the file to seed all the different databases.
    load_drugs()
    load_species_groups()
    load_individual_species()
    load_users()
    load_routes()
    load_conditions()
    load_personal_doses()

    set_val_species_group_id()