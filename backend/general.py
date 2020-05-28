from datetime import datetime
from backend.google_drive import *
from backend.hard_drive import save_month_meta
from backend.slot import Slot
from backend.shift import Shift
from backend.volunteer import Volunteer
from backend.date_utilities import *
from constants import *


# --------------------- initialization -------------------------------------------------------------------------------

def create_new_values():
    spreadsheet = get_spreadsheet_from_drive(SUBMIT_SPREADSHEET)
    dates = get_first_and_last_dates(spreadsheet)
    calendar = create_calendar_dictionary(spreadsheet,  dates[FIRST_D], dates[LAST_D])
    roles = get_roles(spreadsheet)
    volunteers = populate_volunteers(spreadsheet, calendar, roles)

    save_month_meta(dates[FIRST_D], dates[LAST_D])
    auto_assignments(calendar)
    return dates, calendar, volunteers


def get_first_and_last_dates(spreadsheet):
    main_sheet = get_sheet(spreadsheet, MAIN_SHEET)
    main_data = get_data(main_sheet)
    month = main_data[0][MONTH]
    year = main_data[0][YEAR]

    first = get_first_sunday(month, year)
    last = get_last_saturday(month, year)
    return {FIRST_D: first, LAST_D: last}


def get_roles(spreadsheet):
    sheet = get_sheet(spreadsheet, MAIN_SHEET)
    index = get_header(sheet).index('סוגי תפקידים') + 1
    roles = get_column(sheet, index)
    roles.pop(0)
    return roles


# --------------------- calendar initializations ----------------------------------------------------------------------

def get_shifts_dict(spreadsheet):
    main_sheet = get_sheet(spreadsheet, MAIN_SHEET)
    data = get_data(main_sheet)
    day_types = ['שבת', 'שישי', 'חול']
    shifts_dict = {}
    for day_type in day_types:
        shifts_dict.update({day_type: []})
    for row in data:
        day_type = row['יום']
        if day_type != "":
            time = row['משמרת']
            role = row['סוג תפקיד']
            head_count = row['אנשים']
            for i in range(head_count):
                shifts_dict[day_type].append(Shift(time, role, i))
    return shifts_dict


def create_calendar_dictionary(spreadsheet, dt, last_date):
    shifts_dict = get_shifts_dict(spreadsheet)
    calendar = {}
    day = 0

    while dt <= last_date:
        shifts = shifts_dict[get_day_type(dt)]
        day_schedule = []
        for shift in shifts:
            day_schedule.append(Slot(dt, shift.time, shift.role, shift.person, day))
        calendar.update({dt: day_schedule})
        dt = dt + timedelta(days=1)
        day = day + 1

    return calendar


# --------------------- volunteers initializations -------------------------------------------------------------------

def populate_volunteers(spreadsheet, calendar, roles):
    volunteers = {}
    for role in roles:
        some_volunteers = get_volunteers_requests(spreadsheet, role, calendar)
        volunteers.update(some_volunteers)
    return volunteers


def get_volunteers_requests(spreadsheet, role, calendar):
    sheet = get_sheet(spreadsheet, role)
    data = get_data(sheet)
    volunteers = {}
    for row in data:
        volunteer = create_volunteer(calendar, role, row)
        volunteers.update({volunteer.name: volunteer})
    return volunteers


def create_volunteer(calendar, role, row):
    volunteer = Volunteer(row[NAME], row[MAIL], role, row[COMMENTS], row[HALFS], row[MONTHLY],
                          row[WEEKLY_1], row[WEEKLY_2], row[WEEKLY_3], row[WEEKLY_4], row[WEEKLY_5])
    update_volunteer_options(calendar, volunteer, row)
    return volunteer


# ---------------------  updates ---------------------------------------------------------------------------------

def update_volunteer_options(calendar, volunteer, row):
    for day in calendar.keys():
        for slot in calendar[day]:
            if row[str(slot)] != '' and slot.role == volunteer.role:
                volunteer.add_optional_slot(slot)
                slot.add_volunteer(volunteer)


def update_requests_with_minimal_calendar_changes(calendar, volunteers):
    for day in calendar.keys():
        for slot in calendar[day]:
            slot.options = []

    spreadsheet = get_spreadsheet_from_drive(SUBMIT_SPREADSHEET)

    roles = get_roles(spreadsheet)

    for role in roles:
        calendar, volunteers = update_volunteers_requests(spreadsheet, role, calendar, volunteers)

    return calendar, volunteers


def update_volunteers_requests(spreadsheet, role, calendar, volunteers):
    sheet = get_sheet(spreadsheet, role)
    data = get_data(sheet)

    names = volunteers.keys()

    for row in data:
        if row[NAME] in names:
            volunteer = volunteers[row[NAME]]
            volunteer.update_meta_data(row[WEEKLY_1], row[WEEKLY_2], row[WEEKLY_3], row[WEEKLY_4], row[WEEKLY_5], row[MONTHLY], row[COMMENTS])
            update_volunteer_options(calendar, volunteer, row)
            volunteer.remove_invalid_assignments()
        else:
            volunteer = create_volunteer(calendar, role, row)
            volunteers.update({volunteer.name: volunteer})

    return calendar, volunteers


def auto_assignments(calendar):
    for key in calendar.keys():
        for slot in calendar[key]:
            if len(slot.options) == 1:
                volunteer = slot.options[0]
                if volunteer.is_valid_assignment(slot):
                    slot.assign_volunteer(volunteer)






def get_calender_values(calendar, first_date, last_date):
    values = []
    empty_slots = []
    curr_date = first_date
    while curr_date <= last_date:
        time = None
        column = [curr_date.strftime("%-d.%-m.%Y")]
        for slot in calendar[curr_date]:
            if slot.time != time:
                time = slot.time
                column.append(time)
            assignments = slot.get_value()
            if isinstance(assignments, int):
                empty_slots.append(str(slot))
                column.append("")
            else:

                column.append(slot.get_value())
        values.append(column)
        curr_date = curr_date + timedelta(days=1)

    return values, empty_slots


def find_slot_by_drop_down_string(values, calendar):
    date_str = values[0]
    slots = calendar[datetime.strptime(date_str, DATE_FORMAT).date()]
    slot = None
    for s in slots:
        if s.is_drop_down_repr(values):
            slot = s
            break
    if slot is None:
        raise Exception("couldn't find a slot in the calendar for this event?..")
    return slot
