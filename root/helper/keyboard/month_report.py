#!/usr/bin/env python3

""" Function to create the keyboard of the month report """

from root.util.util import get_month_string, create_button


def build_keyboard(month: int, current_month: int, year: int, current_year: int):
    """Build the keyboard for the month report

    Args:
        month (int): the month selected
        current_month (int): the current month of the year
        year (int): the year selected
        current_year (int): the current year
    """
    keyboards = []
    buttons = []
    do_nothing = "empty_button"
    end_emoji = "🔚"

    # ================ FIRST ROW REGARDING MONTH ================
    if month != 1:
        # Set first button to go back a month
        btext = f"{get_month_string(month - 1, False, False )}   ◄"
        bcall = "month_previous_page"
    else:
        # The button goes to December of the previous year
        btext = f"{get_month_string(12, True, False )} {year - 1}   ◄"
        bcall = "month_previous_page"
    buttons.append([[btext, bcall]])

    # The middle button shows the current month
    btext = f"{get_month_string(month, False, False).upper()}"
    bcall = do_nothing
    buttons[0].append([btext, bcall])

    if year == current_year:
        # The user can't pass the current month
        if month == current_month:
            # Set the last button to do nothing as the user cannot go forward with the months
            btext = end_emoji
            bcall = do_nothing
        else:
            btext = f"►   {get_month_string(month + 1, False, False )}"
            bcall = "month_next_page"
    else:
        # The user can pass the current month
        if month != 12:
            # The button goes to January of the next year
            btext = f"►   {get_month_string(month + 1, False, False )}"
            bcall = "month_next_page"
        else:
            btext = f"►   {get_month_string(1, True, False )} {year + 1}"
            bcall = "month_next_page"
    buttons[0].append([btext, bcall])

    # ================ SECOND ROW REGARDING YEAR (1) ================

    # The user can always go back in time regarding years
    btext = f"{get_month_string(month, True, False )} {year - 1}   ◄"
    bcall = "month_previous_year_1"
    buttons.append([[btext, bcall]])

    # The middle button shows the current year
    btext = str(year)
    bcall = do_nothing
    buttons[1].append([btext, bcall])

    # If the user is in the current year he can't go to the next one
    if year == current_year or (month > current_month and year + 1 == current_year):
        btext = end_emoji
        bcall = do_nothing
    else:
        # Otherwise allow him to view the next year
        btext = f"►   {get_month_string(month, True, False )} {year + 1}"
        bcall = "month_next_year_1"
    buttons[1].append([btext, bcall])

    # ================ SECOND ROW REGARDING YEAR (5/10) ================

    # The user can always go back in time regarding years
    btext = "– 10  anni"
    bcall = "month_previous_year_10"
    buttons.append([[btext, bcall]])

    # The user can always go back in time regarding years
    btext = "– 5  anni"
    bcall = "month_previous_year_5"
    buttons[2].append([btext, bcall])

    if year + 5 > current_year:
        # If 5 years from the one viewing goes over the current year block the button
        btext = end_emoji
        bcall = do_nothing
    else:
        # Otherwise allow it
        btext = "+ 5  anni"
        bcall = "month_next_year_5"
    buttons[2].append([btext, bcall])

    if year + 10 > current_year:
        # If 10 years from the one viewing goes over the current year block the button
        btext = end_emoji
        bcall = do_nothing
    else:
        # Otherwise allow it
        btext = "+ 10  anni"
        bcall = "month_next_year_10"
    buttons[2].append([btext, bcall])

    if (not month == current_month and year == current_year) or (year != current_year):
        # Show the button to view the current month/year report if the user is not there
        if (not month + 1 == current_month and year == current_year) or (
            year != current_year
        ):
            btext = (
                f"Vai al mese corrente  ({get_month_string(current_month, False, False)}"
                f" {current_year})"
            )
            bcall = f"expand_report_current_{current_year}"
            # this puts the button at the beginning of the list
            buttons = [[[btext, bcall]], *buttons]

    if not month == 1 and not month == 2:
        bappend = f"  ({year})" if year != current_year else ""
        btext = f"Torna a inizio anno{bappend}"
        bcall = "month_first_month"
        if len(buttons[0]) == 1:
            buttons[0] = [[btext, bcall], *buttons[0]]
        else:
            buttons = [[[btext, bcall]], *buttons]

    # Button to pass to the year report
    btext = f"Passa al report annuale del {year}"
    bcall = f"expand_year_report_{year}"
    buttons.append([[btext, bcall]])

    # Create a telegram compatible keyboard
    for brow in buttons:
        row = [create_button(button[0], button[1], button[1]) for button in brow]
        keyboards.append(row)
    return keyboards
