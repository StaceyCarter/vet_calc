from model import connect_to_db, db, Drug, SpeciesIndividual, Condition
from server import app


def get_vars():
    drug = Drug.query.get(5) # Gets the enrofloxacin drug object
    species = SpeciesIndividual.query.get(2) # Gets the dog object
    condition = Condition.query.get(1) # Returns the None disease query object

    return(drug, species, condition)


def get_species_from_dose(dose):
    """Takes in a dose object and returns the individual and group species it is meant for."""

    indiv = dose.individual_species

    group = dose.species_group

    if indiv.species_individual_id == 1:
        return (1, group.species_group)
    else:
        return (indiv.species_name, group.species_group)


def filter_dose_by_species(drug, species):
    """Find all the doses that relate to a given species.

    Filters out any doses that don't relate to the species of interest. Doses may relate to the individual species
    or the group the species belongs to as a whole.
    Eg. if rat is given as the species, and the drug has doses set specifically for rats it will return these doses.
    Otherwise it will return all the doses related to "small mammals" - the species group associated with the rat object.
    If there are no doses associated with the given species OR species group, send error message.

    :param drug: The drug object of interest
    :type object:

    :param species: The species object of interest
    :type object:

    :returns: A list of doses objects.


    """

    doses = drug.doses

    print(doses)

    dose_correct_species = []

    for dose in doses:
        species_indiv, group = get_species_from_dose(dose)

        #Checks if there was no specific species associated with the dose and looks for equivalence at the group level.
        if species_indiv == 1:
            if group == species.species_group.species_group:
                dose_correct_species.append(dose)
        elif group == species.species_group.species_group:
            dose_correct_species.append(dose)









    return dose_correct_species



#
# doses = drug_obj.doses
# dose_correct_species = []
#

#
# if condition.condition_id != 1:
#     for dose in dose_correct_species:
#         if dose.condition.condition_id == 1:
#             pass




if __name__ == "__main__":
    connect_to_db(app)

    drug, species, condition = get_vars()


