import PySimpleGUI as sg
from backend.general import *
from backend.hard_drive import restore_old_values
from constants import *


def switch_week_window(week_windows, volunteers, new_index, old_index):
    calendar_window = week_windows[new_index]
    refresh_table(calendar_window, volunteers)
    calendar_window.un_hide()
    week_windows[old_index].hide()
    return calendar_window


def create_week_window(first_date, last_date, calendar, volunteers):
    dates = []
    curr_date = last_date
    while curr_date >= first_date:
        column = []
        column += [sg.Text(curr_date.strftime(SHORT_DATE_FORMAT),
                           size=(14, 1), justification='c', font=FONT_14, pad=(5, 0))],
        column += [sg.Text(get_day_name(curr_date.weekday()),
                           size=(18, 1), justification='r', font=FONT_11, pad=(5, 0))],
        time = None
        role_colors = {}
        color_index = 0

        formatted_date = curr_date.strftime(DATE_FORMAT)
        for slot in calendar[curr_date]:
            new_time = slot.time
            if new_time != time:
                column += [sg.Text(new_time, size=(18, 1), justification='r', font=FONT_11,
                                   text_color="white", background_color=sg.theme_button_color()[1])],
                time = new_time

            color = role_colors.get(slot.role)
            if color is None:
                role_colors.update({slot.role: COMBO_COLORS[color_index % 2]})
                color = COMBO_COLORS[color_index % 2]
                color_index = color_index + 1

            column += [sg.Combo(key="{}|{}|{}|{}".format(formatted_date, time, slot.role, slot.person),
                                values=slot.get_names(), default_value=slot.get_value(), enable_events=True,
                                size=(17, 1), pad=(5, 1), font=FONT_11, background_color=color)],
        dates.append(sg.Column(column))
        curr_date = curr_date - timedelta(days=1)

    screen_width, screen_height = sg.Window.get_screen_size()

    table = create_volunteers_table(volunteers, slot.week)
    calendar_window = sg.Window(TITLE, element_justification='c', alpha_channel=0,
                                size=(screen_width-40, screen_height-60), resizable=True).Layout(
        [[sg.Menu([[MENU_TITLE, [MENU_NEW, MENU_SAVE, MENU_UPDATE, MENU_CLOSE]]])],
         [sg.Button(key=B_NEXT, image_filename=IMG_LEFT),
          sg.Column([dates]),
          sg.Button(key=B_PREV, image_filename=IMG_RIGHT)],
         [create_volunteers_header()],
         [table]])

    return calendar_window, table


def pull_data():
    try:
        dates, calendar, volunteers = restore_old_values()
    except:
        dates, calendar, volunteers = create_new_values()
    return dates, calendar, volunteers


def initialize_windows(dates, calendar, volunteers):
    windows = []
    last_date = dates[LAST_D]
    first_date_in_week = dates[FIRST_D]
    last_date_in_week = first_date_in_week + timedelta(days=6)
    while last_date_in_week <= last_date:
        window, table = create_week_window(first_date_in_week, last_date_in_week, calendar, volunteers)
        windows.append(window)
        window.finalize()
        table.expand(False, True, True)
        window.set_alpha(1)
        window.hide()
        first_date_in_week = last_date_in_week + timedelta(days=1)
        last_date_in_week = first_date_in_week + timedelta(days=6)
    return windows, calendar, volunteers


def create_volunteers_header():
    header = [[sg.Text('הערות', font=FONT_11, justification='r', size=(125, 1)),
               sg.Text('חודשי', font=FONT_11, justification='r', size=(10, 1)),
               sg.Text('שם', font=FONT_11, justification='r', size=(15, 1)),
               sg.Text('שבועי', font=FONT_11, justification='r', size=(10, 1))]]
    frame = sg.Frame('מתנדבים', header, font=FONT_12, title_location=sg.TITLE_LOCATION_TOP)
    return sg.Column([[frame]])


def create_volunteers_table(volunteers, week):
    data = [v.get_table_data() for v in volunteers.values()]
    subset = [[v[week-1], v[5], v[6], v[7]] for v in data]
    sorted_volunteers = sorted(subset, key=lambda x: x[0])

    input_rows = [[sg.Text(text=v[2], font=FONT_11, justification='r', size=(125, 1)),
                   sg.Text(text=v[3], font=FONT_11, justification='r', size=(10, 1), key="{}|{}".format(v[1], MONTH_TAG)),
                   sg.Text(text=v[1], font=FONT_LINK, justification='r', size=(15, 1), key="{}|{}".format(NAME_TAG, v[1]), enable_events=True, tooltip="לחץ על מנת לראות שיבוצים"),
                   sg.Text(text=v[0], font=FONT_11, justification='r', size=(10, 1), key="{}|{}".format(v[1], WEEK_TAG))
                   ] for v in sorted_volunteers]

    frame = sg.Frame('',  input_rows, font=FONT_12)
    column = sg.Column([[frame]], scrollable=True, vertical_scroll_only=True)

    return column


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
