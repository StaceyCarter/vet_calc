"""Utility file to seed ratings database from seed files"""


from sqlalchemy import func
from model import Drug, SpeciesGroup
import datetime
from model import connect_to_db, db
from server import app


def load_drugs():
    """Seed data from drug_seed.psv into the drugs table of the database

    File format:
    Drug name | interactions | contraindications

    """

    print("Drugs")

    Drug.query.delete()

    with open("seed_data/drug_seed.psv") as drugs:
        for row in drugs:
            name, interactions, contraindications = row.strip().split("|")

            drug = Drug(generic_name=name,
                        interactions=interactions,
                        contraindications=contraindications)

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
    set_val_species_group_id()
