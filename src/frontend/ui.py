from datetime import timedelta
import PySimpleGUI as sg
from src.utils.dates import get_day_name
from src.utils.constants import *


def switch_week_window(week_windows, volunteers, new_index, old_index):
    calendar_window = week_windows[new_index]
    refresh_table(calendar_window, volunteers)
    calendar_window.un_hide()
    week_windows[old_index].hide()
    return calendar_window


def create_week_window(first_date, last_date, data):
    dates = []
    curr_date = last_date
    while curr_date >= first_date:
        column = []
        column += [sg.Text(curr_date.strftime(SHORT_DATE_FORMAT),
                           size=(12, 1), justification='c', font=FONT_14, pad=(5, 0))],
        column += [sg.Text(get_day_name(curr_date.weekday()),
                           size=(15, 1), justification='r', font=FONT_11, pad=(5, 0))],
        time = None
        role_colors = {}
        color_index = 0

        formatted_date = curr_date.strftime(DATE_FORMAT)
        for slot in data.calendar.slots_by_date[curr_date]:
            new_time = slot.time
            if new_time != time:
                column += [sg.Text(new_time, size=(15, 1), justification='r', font=FONT_11,
                                   text_color="white", background_color=TIME_COLOR)],
                time = new_time

            color = role_colors.get(slot.role)
            if color is None:
                role_colors.update({slot.role: COMBO_COLORS[color_index % 2]})
                color = COMBO_COLORS[color_index % 2]
                color_index = color_index + 1

            column += [sg.Combo(key="{}|{}|{}|{}".format(formatted_date, time, slot.role, slot.person),
                                values=slot.get_names(), default_value=slot.get_value(), enable_events=True,
                                size=(14, 1), pad=(5, 1), font=FONT_11, background_color=color)],
        dates.append(sg.Column(column))
        curr_date = curr_date - timedelta(days=1)

    screen_width, screen_height = sg.Window.get_screen_size()
    week = slot.week

    table = create_volunteers_table(data.volunteers, week)
    list_frame = sg.Frame('', [[create_volunteers_header()], [table]])

    details_combo, details = create_details(data.volunteers, week)
    details_frame = sg.Frame('', [[details_combo], [details]])

    calendar_window = sg.Window(TITLE, element_justification='c', alpha_channel=0, location=(0, 0),
                                size=(screen_width-40, screen_height-80), resizable=True).Layout(
        [[sg.Menu([[MENU_TITLE_1, [MENU_SAVE, MENU_UPDATE, MENU_ASSIGN]],
                   [MENU_TITLE_2, [MENU_UPLOAD, MENU_PUBLISH, MENU_NEW]]])],
         [sg.Button(key=B_NEXT, image_filename=IMG_LEFT),
          sg.Column([dates]),
          sg.Button(key=B_PREV, image_filename=IMG_RIGHT)],
         [list_frame, details_frame]])

    calendar_window.finalize()
    calendar_window.set_alpha(1)
    calendar_window.hide()

    table.expand(False, True, True)
    details_frame.expand(False, True, True)
    details.expand(False, True, True)

    return calendar_window


def initialize_windows(data):
    windows = []
    last_date = data.calendar.last_date
    first_date_in_week = data.calendar.first_date
    last_date_in_week = first_date_in_week + timedelta(days=6)
    while last_date_in_week <= last_date:
        window = create_week_window(first_date_in_week, last_date_in_week, data)
        windows.append(window)

        first_date_in_week = last_date_in_week + timedelta(days=1)
        last_date_in_week = first_date_in_week + timedelta(days=6)
    return windows


def create_volunteers_header():
    header = [[sg.Text('הערות', font=FONT_11, justification='r', size=(40, 1)),
               sg.Text('חודשי', font=FONT_11, justification='r', size=(6, 1)),
               sg.Text('שם', font=FONT_11, justification='r', size=(15, 1)),
               sg.Text('שבועי', font=FONT_11, justification='r', size=(6, 1)),
               sg.Text('אופציות', font=FONT_11, justification='r', size=(5, 1))]]
    frame = sg.Frame('מתנדבים', header, font=FONT_12, title_location=sg.TITLE_LOCATION_TOP)
    return sg.Column([[frame]])


def create_volunteers_table(volunteers, week):
    data = [v.get_table_data() for v in volunteers.values()]
    subset = [[v[week-1][1], v[week-1][0], v[5], v[6], v[7]] for v in data]
    sorted_volunteers = sorted(subset)

    input_rows = [[sg.Text(text=v[3], font=FONT_11, justification='r', size=(40, 1)),
                   sg.Text(text=v[4], font=FONT_11, justification='r', size=(6, 1), key="{}|{}".format(v[2], MONTH_TAG)),
                   sg.Text(text=v[2], font=FONT_LINK, justification='r', size=(15, 1), key="{}|{}".format(NAME_TAG, v[2]), enable_events=True, tooltip="לחץ על מנת לראות שיבוצים"),
                   sg.Text(text=v[1], font=FONT_11, justification='r', size=(6, 1), key="{}|{}".format(v[2], WEEK_TAG)),
                   sg.Text(text=v[0], font=FONT_11, justification='r', size=(5, 1))
                   ] for v in sorted_volunteers]

    frame = sg.Frame('',  input_rows, font=FONT_12)
    column = sg.Column([[frame]], scrollable=True, vertical_scroll_only=True)

    return column

def create_details(volunteers, week):
    names = [*volunteers]
    names.sort()
    default = names[0]
    input_rows = []

    input_rows += [sg.Multiline(default_text=volunteers[default].comments, key="details_comments",
                                size=(50, 3), enable_events=False, font=FONT_11)],
    input_rows += [sg.Text(volunteers[default].get_weekly_and_monthly_str(week), key="details_requests",
                        size=(50, 1), justification='r', font=FONT_11)],
    input_rows += [sg.Text(volunteers[default].get_options_as_string(week), key="details_options",
                       size=(50, 7), justification='r', font=FONT_11)],
    input_rows += [sg.Text(volunteers[default].get_assignments_as_string(week), key="details_assignments",
                       size=(50, 7), justification='r', font=FONT_11)],
    column = sg.Column(input_rows, scrollable=True, vertical_scroll_only=True)

    combo = sg.Combo(key=SEARCH, values=names, default_value=default, enable_events=True, size=(50, 1), font=FONT_11)
    combo_frame = sg.Frame('', [[combo]], font=FONT_12, title_location=sg.TITLE_LOCATION_TOP)

    return combo_frame, column


def update_details(week_windows, volunteer):
    for week in range(0, len(week_windows)):
        week_windows[week][SEARCH].update(value=volunteer.name)
        week_windows[week]["details_comments"].update(value=volunteer.comments)
        week_windows[week]["details_requests"].update(value=volunteer.get_weekly_and_monthly_str(week+1))
        week_windows[week]["details_options"].update(value=volunteer.get_options_as_string(week+1))
        week_windows[week]["details_assignments"].update(value=volunteer.get_assignments_as_string(week+1))


def refresh_details(week_windows, volunteers):
    volunteer = volunteers[week_windows[0][SEARCH].get()]
    for week in range(0, len(week_windows)):
        week_windows[week]["details_requests"].update(value=volunteer.get_weekly_and_monthly_str(week+1))
        week_windows[week]["details_assignments"].update(value=volunteer.get_assignments_as_string(week+1))



def update_window(window, volunteers, week, combobox, text):
    for volunteer in volunteers:
        element_week = window["{}|{}".format(volunteer.name, WEEK_TAG)]
        element_week.update(value=volunteer.weekly_status(week))

        element_month = window["{}|{}".format(volunteer.name, MONTH_TAG)]
        element_month.update(value=volunteer.monthly_status())

    window[combobox].update(value="")
    window[combobox].update(value=text)


def refresh_table(window, volunteers):
    for volunteer in volunteers.values():
        element_month = window["{}|{}".format(volunteer.name, MONTH_TAG)]
        element_month.update(value=volunteer.monthly_status())
