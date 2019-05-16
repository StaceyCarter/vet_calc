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
    dose(mg/kg) - Float
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


def get_num_tablets_per_dose(dose, strength, divisions=1):
    """Calculates the number of tablets to give based on the dose given and the strength of the tablets.

    Tablets can be divided in quarters.

    :params:
    dose (Float) - The dose in mg of what the patient should be receiving
    strength (Float) - The strength in mg of the chosen tablets.
    divisions (Int) - the number of sections you can divide your tablet into

    :returns:
    Number of tablets per dose (Float) - fixed to one of the points of the divisions

    >>> get_num_tablets_per_dose(120, 100, 2)
    1.0

    >>> get_num_tablets_per_dose(240, 100, 2)
    2.5

    #Divide into quarters
    >>> get_num_tablets_per_dose(120, 100, 4)
    1.25

    """

    num_tabs = dose/strength

    return round(num_tabs * divisions)/divisions


def total_amount_needed(amount, duration, frequency):
    """Calculates the total amount of the drug that is needed to send home with the client.

    Params:
    amount(Float) - Could be in mls or the number of tablets per dose.
    duration(Integer) - The number of days to give the medication for
    frequency(Integer) - The interval between each dosing in hrs.

    :returns:
    Total amount of the drug(float) (either in mls or number of tablets) to be sent home.

    >>> total_amount_needed(0.5, 7, 12)
    7.0

    >>> total_amount_needed(1.5, 14, 8)
    63.0

    >>> total_amount_needed(2, 60, 48)
    60.0
    """

    # Number of times per day * days of treatment * amount per each dose
    return 24 / frequency * duration * amount

def get_instructions(weight, dose, concentration, duration, frequency, form, divide=1):
    """Take in arguments obtained from the input form and output a dictionary with points of interest.

    :params:

    weight (Float)
    dose(mg/kg) (Float)
    duration - number of days to continue treatment (Int)
    frequency - how many hours in between each treatment (Int)
    concentration - concentration of the drug (mg/ml) being used (Float)

    :returns:
    Dictionary with information on amount to give per dose, the total amount to send home, how many hours to leave
    between each dose and the frequency of the dose per day.

    Examples:
    >>> get_instructions(10, 2, 0.5, 7, 12, 'liq')
    {'amount_per_dose': 40.0, 'total_amount': 560.0, 'frequency_hrs': 12, 'frequency_day': '2 times daily', 'duration': 7, 'form': 'liq'}

    >>> get_instructions(50, 2.5, 100, 14, 8, 'tab', 4)
    {'amount_per_dose': 1.25, 'total_amount': 52.5, 'frequency_hrs': 8, 'frequency_day': '3 times daily', 'duration': 14, 'form': 'tab'}
    """

    amount_in_mg = get_amount_in_mg(weight, dose)

    amount_per_dose = 0

    if form == 'liq':
        amount_per_dose = get_amount_in_ml(amount_in_mg, concentration)
    elif form == 'tab':
        amount_per_dose = get_num_tablets_per_dose(amount_in_mg, concentration, divide)

    total_amount = total_amount_needed(amount_per_dose, duration, frequency)

    frequency_per_day = 24/frequency

    if frequency_per_day == 0.5:
        frequency_day = "Every other day"
    elif round(frequency_per_day,2) == 0.33:
        frequency_day = "Every 3rd day"
    else:
        frequency_day = f"{int(frequency_per_day)} times daily"


    instruction_info = {
        'amount_per_dose' : round(amount_per_dose,2),
        'total_amount' : round(total_amount,2),
        'frequency_hrs' : int(frequency),
        'frequency_day' : frequency_day,
        'duration' : int(duration),
        'form' : form
    }

    return instruction_info



if __name__ == "__main__":
    from doctest import testmod
    if testmod().failed == 0:
        print("ALL DOCTESTS TESTS PASSED!")

