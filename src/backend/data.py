from src.backend.calendar import Calendar
from src.utils.constants import *
from src.utils.emails import send_email
from src.utils.google_drive import *
from src.backend.volunteer import Volunteer


class Data:

    def __init__(self):
        self.spreadsheet = None
        self.roles = None

        self.update_spreadsheet()
        self.update_roles()

        self.calendar = Calendar(self.spreadsheet)
        self.volunteers = self.populate_volunteers()


    def update_spreadsheet(self):
        self.spreadsheet = get_spreadsheet_from_drive(SUBMIT_SPREADSHEET)

    def update_roles(self):
        sheet = get_sheet(self.spreadsheet, MAIN_SHEET)
        index = get_header(sheet).index('סוגי תפקידים') + 1
        roles = get_column(sheet, index)
        roles.pop(0)
        self.roles = roles

    def populate_volunteers(self):
        volunteers = {}
        for role in self.roles:
            some_volunteers = self.get_volunteers_requests(role)
            volunteers.update(some_volunteers)
        return volunteers

    def get_volunteers_requests(self, role):
        sheet = get_sheet(self.spreadsheet, role)
        data = get_data(sheet)[1:]
        volunteers = {}
        for row in data:
            volunteer = self.create_volunteer(role, row)
            volunteers.update({volunteer.name: volunteer})
        return volunteers

    def get_volunteers_names(self):
        return self.volunteers.keys()

    def create_volunteer(self, role, row):
        volunteer = Volunteer(row[NAME], row[MAIL], role, row[COMMENTS], row[HALFS], row[MONTHLY],
                              row[WEEKLY_1], row[WEEKLY_2], row[WEEKLY_3], row[WEEKLY_4], row[WEEKLY_5])
        self.update_volunteer_options(volunteer, row)
        return volunteer

    def update_volunteer_options(self, volunteer, row):
        for day in self.calendar.slots_by_date.keys():
            for slot in self.calendar.slots_by_date[day]:
                if row[str(slot)] != '' and slot.role == volunteer.role:
                    volunteer.add_optional_slot(slot)
                    slot.add_volunteer(volunteer)

    def update_requests_with_minimal_calendar_changes(self):
        for day in self.calendar.slots_by_date.keys():
            for slot in self.calendar.slots_by_date[day]:
                slot.options = []

        self.update_spreadsheet()
        self.update_roles()

        for role in self.roles:
            self.update_volunteers_requests(role)

    def update_volunteers_requests(self, role):
        sheet = get_sheet(self.spreadsheet, role)
        data = get_data(sheet)[1:]

        names = self.volunteers.keys()

        for row in data:
            if row[NAME] in names:
                volunteer = self.volunteers[row[NAME]]
                volunteer.update_meta_data(row[WEEKLY_1], row[WEEKLY_2], row[WEEKLY_3], row[WEEKLY_4], row[WEEKLY_5],
                                           row[MONTHLY], row[COMMENTS], row[HALFS])
                self.update_volunteer_options(volunteer, row)
                volunteer.remove_invalid_assignments()
            else:
                volunteer = self.create_volunteer(role, row)
                self.volunteers.update({volunteer.name: volunteer})

    def auto_assignments(self):
        for key in self.calendar.slots_by_date.keys():
            for slot in self.calendar.slots_by_date[key]:
                if len(slot.assignment) == 0 and len(slot.options) == 1:
                    volunteer = slot.options[0]
                    if volunteer.is_valid_assignment(slot):
                        slot.assign_volunteer(volunteer)
        for volunteer in self.volunteers.values():
            for week in range(1, 6):
                if int(volunteer.weekly_options(week)) == 1:
                    if volunteer.assigned_slots[week][0] == 0:
                        slots = volunteer.optional_slots[week][1]
                        i = 0
                        while i < len(slots):
                            slot = slots[i]
                            if len(slot.assignment) == 0 and volunteer.is_valid_assignment(slot):
                                slot.assign_volunteer(volunteer)
                                i = len(slots)
                            i += 1

    def publish_shifts(self):
        root_text = "<p dir='rtl'> פורסמו המשמרות לחודש הבא. ניתן למצוא את לוח המשמרות המלא כאן: {}<br><br>המשמרות שלך:<br>".format(
            SHIFTS_LINK)
        for name in self.volunteers.keys():
            message_text = root_text
            volunteer = self.volunteers[name]
            for week in volunteer.assigned_slots:
                volunteer.assigned_slots[week][1].sort(key=lambda s: (s.date, s.time))
                for slot in volunteer.assigned_slots[week][1]:
                    message_text += "{}<br>".format(str(slot).replace(" ", "   "))
            message_text += "</p>"
            send_email(volunteer.email, "משמרות סהר", message_text)
