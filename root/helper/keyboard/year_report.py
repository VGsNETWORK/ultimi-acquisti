#!/usr/bin/env python3

""" Function to create the keyboard of the year report """

from root.util.util import create_button


def build_keyboard(year: int, current_year: int):
    """Build the keyboard for the year report

    Args:
        year (int): the year selected
        current_year (int): the current year
    """
    keyboards = []
    buttons = []
    do_nothing = "empty_button"
    end_emoji = "🔚"
    # ================ FIRST ROW REGARDING YEAR ================
    # FIRST BUTTON OF FIRST ROW
    btext = f"{year - 1}   ◄"
    bcall = "year_previous_year_1"
    buttons.append([[btext, bcall]])

    # SECOND BUTTON OF FIRST ROW
    btext = f"{year}"
    bcall = do_nothing
    buttons[0].append([btext, bcall])

    # THIRD BUTTON OF FIRST ROW
    if year != current_year:
        btext = f"►   {year + 1}"
        bcall = "year_next_year_1"
    else:
        btext = end_emoji
        bcall = do_nothing
    buttons[0].append([btext, bcall])

    # ================ SECOND ROW REGARDING YEAR ================

    # The user can always go back in time regarding years
    btext = "– 10  anni"
    bcall = "year_previous_year_10"
    buttons.append([[btext, bcall]])

    # The user can always go back in time regarding years
    btext = "– 5  anni"
    bcall = "year_previous_year_5"
    buttons[1].append([btext, bcall])

    # If the user is less than 5 years ago do not allow him to proceed
    if year + 5 > current_year:
        btext = end_emoji
        bcall = do_nothing
    else:
        # Otherwise allow him to view the next year
        btext = "+ 5  anni"
        bcall = "year_next_year_5"
    buttons[1].append([btext, bcall])

    # If the user is less than 10 years ago do not allow him to proceed
    if year + 10 > current_year:
        btext = end_emoji
        bcall = do_nothing
    else:
        # Otherwise allow him to view the next year
        btext = "+ 10  anni"
        bcall = "year_next_year_10"
    buttons[1].append([btext, bcall])

    # ================ THIRD ROW REGARDING YEAR ================
    btext = f"Passa al report mensile di Gennaio {year}"
    bcall = f"expand_report_{year}"
    buttons.append([[btext, bcall]])

    #  =============== FIRST ROW REGARDING CURRENT YEAR ====================
    if not current_year in (year + 1, year):
        btext = f"Vai all'anno corrente  ({current_year})"
        bcall = f"year_next_year_{current_year-year}"
        buttons = [[[btext, bcall]], *buttons]

    # Create a telegram compatible keyboard
    for brow in buttons:
        row = [create_button(button[0], button[1], button[1]) for button in brow]
        keyboards.append(row)
    return keyboards
