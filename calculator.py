def lbs_to_kg(weight):
    """convert a weight in pounds to a weight in kg

    :params:
    weight(lbs) - Float

    :returns:
    weight(kg) - Float

    Examples:
    >>> lbs_to_kg(10)
    4.535923700000001

    >>> lbs_to_kg(100)
    45.359237

    """

    return weight * 0.45359237


def get_amount_in_mg(weight, dose):
    """Calculates the amount of drug needed in mg for a given weight and dose.

    :params:
    weight - Float
    dose - Float

    :returns:
    Float - amount of drug needed in mg.

    Examples:
    >>> get_amount_in_mg(10.2, 13.75)
    140.25

    >>> get_amount_in_mg(5, 0.5)
    2.5

    """

    return weight * dose

def get_amount_in_ml(dose, concentration):
    """Calculates the amount of liquid drug to be given in mls, given a dose(mg/kg) and concentration (mg/ml.

    :params:
    dose - Float
    concentration - Float

    :returns:
    Amount in mls - Float

    Examples:
    >>> get_amount_in_ml(2.5, 50)
    0.05

    >>> get_amount_in_ml(80, 50)
    1.6
    """

    return dose/concentration

#!!!! - NEEDS FINISHING
def calc_num_tablets(dose, strength):
    """Calculates the number of tablets to give based on the dose given and the strength of the tablets.

    Tablets can be divided in quarters.

    :params:
    dose (Float) - The dose in mg of what the patient should be receiving
    strength (Float) - The strength in mg of the chosen tablets.

    :returns:

    """




def calc_amount_needed(amount, duration, frequency):
    """Calculates the total amount of the drug that is needed to send home with the client.

    :params:
    amount(Float) - The amount of drug to be given each dose in mls
    duration(Integer) - The number of days to give the medication for
    frequency(Integer) - The interval between each dosing in hrs.

    :returns:
    Total amount of the drug(float) (either in mls or number of tablets) to be sent home.

    >>> calc_amount_needed(0.5, 7, 12)
    7.0

    >>> calc_amount_needed(1.5, 14, 8)
    63.0

    >>> calc_amount_needed(2, 60, 48)
    60.0
    """

    return 24 / frequency * duration * amount



if __name__ == "__main__":
    from doctest import testmod
    if testmod().failed == 0:
        print("ALL DOCTESTS TESTS PASSED!")

