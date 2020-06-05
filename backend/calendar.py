from utils.google_drive import get_sheet, get_data
from utils.constants import MAIN_SHEET, MONTH, YEAR, DATE_FORMAT
from utils.dates import get_first_sunday, get_last_saturday, get_day_type
from backend.shift import Shift
from backend.slot import Slot
from datetime import timedelta, datetime


class Calendar:

    def __init__(self, spreadsheet):
        month, year = self.get_month_and_year(spreadsheet)

        self.first_date = get_first_sunday(month, year)
        self.last_date = get_last_saturday(month, year)
        self.shifts_dict = self.get_shifts_dict(spreadsheet)
        self.slots_by_date = {}

        day = 0
        dt = self.first_date
        while dt <= self.last_date:
            shifts = self.shifts_dict[get_day_type(dt)]
            day_schedule = []
            for shift in shifts:
                day_schedule.append(Slot(dt, shift.time, shift.role, shift.person, day))
            self.slots_by_date.update({dt: day_schedule})
            dt = dt + timedelta(days=1)
            day = day + 1

    def get_month_and_year(self, spreadsheet):
        main_sheet = get_sheet(spreadsheet, MAIN_SHEET)
        main_data = get_data(main_sheet)
        month = main_data[0][MONTH]
        year = main_data[0][YEAR]
        return month, year


    def get_shifts_dict(self, spreadsheet):
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


    def get_calender_values(self):
        values = []
        empty_slots = []
        curr_date = self.first_date
        while curr_date <= self.last_date:
            time = None
            column = [curr_date.strftime("%-d.%-m.%Y")]
            for slot in self.slots_by_date[curr_date]:
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


    def find_slot_by_drop_down_string(self, values):
        date_str = values[0]
        slots = self.slots_by_date[datetime.strptime(date_str, DATE_FORMAT).date()]
        slot = None
        for s in slots:
            if s.is_drop_down_repr(values):
                slot = s
                break
        if slot is None:
            raise Exception("couldn't find a slot in the calendar for this event?..")
        return slot
