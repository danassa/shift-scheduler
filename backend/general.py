from backend.drive import *
from backend.slot import Slot
from backend.shift import Shift
from backend.volunteer import Volunteer
from backend.utilities import *
import dill
from constants import LAST_D, FIRST_D, DATE_FORMAT, META_FILE, VOLUNTEERS_FILE, CALENDAR_FILE, SUBMIT_SPREADSHEET, SCHEDULE_SPREADSHEET


def auto_assignments(calendar):
    for key in calendar.keys():
        for slot in calendar[key]:
            if len(slot.options) == 1:
                volunteer = slot.options[0]
                if volunteer.is_valid_assignment(slot):
                    slot.assign_volunteer(volunteer)


def create_shifts_dict(data, day_types):
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


def get_dates(spreadsheet):
    main = 'Manager'
    main_sheet = get_sheet(spreadsheet, main)
    main_data = get_data(main_sheet)
    month = main_data[0]['חודש']
    year = main_data[0]['שנה']

    first = get_first_sunday(month, year)
    last = get_last_saturday(month, year)
    return {FIRST_D: first, LAST_D: last}


def create_calendar(spreadsheet, dt, last_date):
    main = 'Manager'
    main_sheet = get_sheet(spreadsheet, main)
    data = get_data(main_sheet)
    day_types = ['שבת', 'שישי', 'חול']
    shifts_dict = create_shifts_dict(data, day_types)

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


def create_volunteers_requests(spreadsheet, role, calendar):
    sheet = get_sheet(spreadsheet, role)
    data = get_data(sheet)
    volunteers = {}
    for row in data:
        volunteer = create_volunteer(calendar, role, row)
        volunteers.update({volunteer.name: volunteer})
    return volunteers


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


def get_roles(spreadsheet):
    sheet = get_sheet(spreadsheet, 'Manager')
    index = get_header(sheet).index('סוגי תפקידים') + 1
    roles = get_column(sheet, index)
    roles.pop(0)
    return roles


def update_volunteers_requests(spreadsheet, role, calendar, volunteers):
    sheet = get_sheet(spreadsheet, role)
    data = get_data(sheet)

    names = volunteers.keys()

    for row in data:
        if row['שם'] in names:
            volunteer = volunteers[row['שם']]
            volunteer.update_meta_data(row['שבועי 1'], row['שבועי 2'], row['שבועי 3'], row['שבועי 4'], row['שבועי 5'], row['חודשי'], row['הערות'])
            update_volunteer_options(calendar, volunteer, row)
            volunteer.remove_invalid_assignments()
        else:
            volunteer = create_volunteer(calendar, role, row)
            volunteers.update({volunteer.name: volunteer})

    return calendar, volunteers


def update_volunteer_options(calendar, volunteer, row):
    for day in calendar.keys():
        for slot in calendar[day]:
            if row[str(slot)] != '' and slot.role == volunteer.role:
                volunteer.add_optional_slot(slot)
                slot.add_volunteer(volunteer)


def create_volunteer(calendar, role, row):
    volunteer = Volunteer(row['שם'], row['מייל'], role, row['הערות'], row['חצאי משמרות'], row['חודשי'],
                          row['שבועי 1'], row['שבועי 2'], row['שבועי 3'], row['שבועי 4'], row['שבועי 5'])
    update_volunteer_options(calendar, volunteer, row)
    return volunteer


def create_data_structures(spreadsheet, first, last):
    calendar = create_calendar(spreadsheet, first, last)
    roles = get_roles(spreadsheet)
    volunteers = {}
    for role in roles:
        some_volunteers = create_volunteers_requests(spreadsheet, role, calendar)
        volunteers.update(some_volunteers)

    save_month_meta(first, last)
    return calendar, volunteers


def save_month_meta(first, last):
    with open(META_FILE, "wb") as dill_file:
        dill.dump({FIRST_D: first, LAST_D: last}, dill_file)


def save(calendar, volunteers):
    with open(CALENDAR_FILE, "wb") as dill_file:
        dill.dump(calendar, dill_file)
    with open(VOLUNTEERS_FILE, "wb") as dill_file:
        dill.dump(volunteers, dill_file)


def restore_old_values():
    with open(META_FILE, "rb") as dill_file:
        dates = dill.load(dill_file)
    with open(CALENDAR_FILE, "rb") as dill_file:
        calendar = dill.load(dill_file)
    with open(VOLUNTEERS_FILE, "rb") as dill_file:
        volunteers = dill.load(dill_file)

    return dates, calendar, volunteers


def create_new_values():
    spreadsheet = get_sheets_from_drive(SUBMIT_SPREADSHEET)
    dates = get_dates(spreadsheet)
    calendar, volunteers = create_data_structures(spreadsheet, dates[FIRST_D], dates[LAST_D])
    auto_assignments(calendar)
    return dates, calendar, volunteers


def update_requests_with_minimal_calendar_changes(calendar, volunteers):
    for day in calendar.keys():
        for slot in calendar[day]:
            slot.options = []

    spreadsheet = get_sheets_from_drive(SUBMIT_SPREADSHEET)

    roles = get_roles(spreadsheet)

    for role in roles:
        calendar, volunteers = update_volunteers_requests(spreadsheet, role, calendar, volunteers)

    return calendar, volunteers


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


def publish(values, first_date):
    spreadsheet = get_sheets_from_drive(SCHEDULE_SPREADSHEET)
    update_schedule_sheet(spreadsheet, values, first_date)


def email(volunteers, url):
    credentials = get_email_credentials()
    service = build('gmail', 'v1', credentials=credentials)
    root_test = "<p dir='rtl'> פורסמו המשמרות לחודש הבא. ניתן למצוא את לוח המשמרות המלא כאן: {}<br><br>המשמרות שלך:<br>".format(url)
    message_text = root_test
    for name in volunteers.keys():
        volunteer = volunteers[name]
        for week in volunteer.assigned_slots:
            for slot in volunteer.assigned_slots[week][1]:
                message_text += "{}<br>".format(str(slot))
        message_text += "</p>"
        send_email(service, [volunteer.email], "משמרות סהר", message_text)
        message_text = root_test
