from model import connect_to_db, db, Drug, SpeciesIndividual, Condition, PersonalDose


def filter_dose_using_species(drug, species):
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

    :returns: A list of doses objects or an error message as a string.


    """
    doses = drug.doses

    species_filter = filter_dose_by_individual_species(doses, species)
    group_filter = filter_dose_by_species_group(doses, species)

    if species_filter:
        return species_filter
    elif group_filter:
        return group_filter
    else:
        return "Sorry, we can't find any doses in the database for that species."


def filter_dose_by_individual_species(doses, species):
    """Filter out relevent doses by the species name

    If it does find doses with the specific species name, it returns a list of these.
    If it doesn't find any doses with the specific species name, it returns None.

    :param doses: A list of dose objects
    :type list:

    :param species:
    :type string:

    :returns: either None or a list of dose objects
    """

    relevant_doses = []

    for dose in doses:
        if dose.individual_species.species_name == species.species_name:
            relevant_doses.append(dose)

    return relevant_doses



def filter_dose_by_species_group(doses, species):
    """Filter out doses by the species group name

    If it does find doses with the group name, it returns a list of these.
    If it doesn't find any doses with the specific species name, it returns an error message for the user.

    :param doses: A list of dose objects
    :type list:

    :param species:
    :type string:

    :returns: either None or a list of dose objects
    """
    relevant_doses = []

    for dose in doses:
        if dose.species_group.species_group == species.species_group.species_group:
            relevant_doses.append(dose)

    return relevant_doses






