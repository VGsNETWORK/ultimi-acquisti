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
    bcall = "year_previous_year"
    buttons.append([[btext, bcall]])

    # SECOND BUTTON OF FIRST ROW
    btext = f"{year}"
    bcall = do_nothing
    buttons[0].append([btext, bcall])

    # THIRD BUTTON OF FIRST ROW
    if year != current_year:
        btext = f"►   {year + 1}"
        bcall = "year_next_year"
    else:
        btext = end_emoji
        bcall = do_nothing
    buttons[0].append([btext, bcall])

    # ================ SECOND ROW REGARDING YEAR ================
    btext = f"Passa al report mensile di Gennaio {year}"
    bcall = f"expand_report_{year}"
    buttons.append([[btext, bcall]])

    # Create a telegram compatible keyboard
    for brow in buttons:
        row = [create_button(button[0], button[1], button[1]) for button in brow]
        keyboards.append(row)
    return keyboards
