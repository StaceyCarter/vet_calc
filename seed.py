"""Utility file to seed ratings database from seed files"""

from model import Drug

from model import connect_to_db, db
from server import app

def load_drugs():
    """Seed data from drug_seed.psv into the drugs table of the database"""

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



if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Run functions in the file to seed all the different databases.
    load_drugs()
