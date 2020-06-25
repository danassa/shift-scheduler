import logging
from src.utils.dates import get_day_name
from collections import defaultdict


class Volunteer:

    def __init__(self, name, email, role, comments, privileged, monthly, weekly1, weekly2, weekly3, weekly4, weekly5):
        self.name = name
        self.email = email
        self.role = role
        self.comments = comments
        self.monthly_requests = self.validate_input(monthly, 100)
        self.privileged = privileged == "TRUE"
        self.optional_slots = {
            1: [self.validate_input(weekly1, self.monthly_requests), []],
            2: [self.validate_input(weekly2, self.monthly_requests), []],
            3: [self.validate_input(weekly3, self.monthly_requests), []],
            4: [self.validate_input(weekly4, self.monthly_requests), []],
            5: [self.validate_input(weekly5, self.monthly_requests), []]
        }
        self.assigned_slots = {
            1: [0, []],
            2: [0, []],
            3: [0, []],
            4: [0, []],
            5: [0, []]
        }
        self.total_shifts = 0

    def validate_input(self, requests, default):
        try:
            result = int(requests)
            return result
        except:
            return default

    def add_optional_slot(self, slot):
        week = self.optional_slots[slot.week]
        week[1].append(slot)

    def clear_optional_slots(self, weekly1, weekly2, weekly3, weekly4, weekly5):
        self.optional_slots = {
            1: [weekly1, []],
            2: [weekly2, []],
            3: [weekly3, []],
            4: [weekly4, []],
            5: [weekly5, []]
        }

    def update_meta_data(self, weekly1, weekly2, weekly3, weekly4, weekly5, monthly, comments):
        self.clear_optional_slots(weekly1, weekly2, weekly3, weekly4, weekly5)
        self.monthly_requests = monthly
        self.comments = comments

    ##############################################################

    def remove_invalid_assignments(self):
        for week in self.assigned_slots:
            for slot in self.assigned_slots[week][1]:
                if slot not in self.optional_slots[week][1]:
                    slot.release_assignment()

    def remove_optional_slot(self, slot, week):
        for s in self.optional_slots[week][1]:
            if str(s) == str(slot):
                self.remove_slot(s)

    def assign_slot(self, slot):
        week = self.assigned_slots[slot.week]
        week[0] = week[0] + 1
        week[1].append(slot)
        self.total_shifts = self.total_shifts + 1

    def remove_slot(self, slot):
        week = self.assigned_slots[slot.week]
        week[0] = week[0] - 1
        week[1].remove(slot)
        self.total_shifts = self.total_shifts - 1

    def is_valid_assignment(self, slot, gui_queue=None):
        error = None
        if self.total_shifts >= self.monthly_requests:
            error = "מספר המשמרות החודשי של {} חוצה את {} המשמרות המבוקשות".format(self.name, self.monthly_requests)
        elif self.assigned_slots[slot.week][0] >= self.optional_slots[slot.week][0]:
            error = "מספר המשמרות השבועי של {} חוצה את {} המשמרות המבוקשות".format(self.name, self.optional_slots[slot.week][0])
        else:
            for week in self.assigned_slots.values():
                for curr_slot in week[1]:
                    delta = (curr_slot.date - slot.date).days
                    if -1 <= delta <= 1 and curr_slot != slot: #todo
                        error = "{} משובץ/ת למשמרת בתאריך {}".format(self.name, curr_slot.date)

        if gui_queue is not None and error is not None:
            logging.error(error)
            gui_queue.put(error)
        return error is None

    def weekly_status(self, week):
        return "{}/{}".format(self.assigned_slots[week][0], self.optional_slots[week][0])

    def monthly_status(self):
        return "{}/{}".format(self.total_shifts, self.monthly_requests)

    def weekly_options(self, week):
        res = map(lambda x: str(x), self.optional_slots[week][1])
        return "{}".format(len(set(res)))

    def get_table_data(self):
        data = [[self.weekly_status(1), self.weekly_options(1)],
                [self.weekly_status(2), self.weekly_options(2)],
                [self.weekly_status(3), self.weekly_options(3)],
                [self.weekly_status(4), self.weekly_options(4)],
                [self.weekly_status(5), self.weekly_options(5)],
                self.name,
                self.comments,
                self.monthly_status()
                ]
        return data

    def get_options_as_string(self, week):
        slots = self.optional_slots[week][1]
        result = self.get_list_by_day(slots, '\nאופציות שהוגשו השבוע:\n')
        return result

    def get_assignments_as_string(self, week):
        slots = self.assigned_slots[week][1]
        result = self.get_list_by_day(slots, '\nשיבוצים השבוע:\n')
        return result

    def get_list_by_day(self, slots, result):
        per_day_dict = defaultdict(set)
        for s in slots:
            day = get_day_name(s.date.weekday())
            per_day_dict[day].add(s.time)
        for key, value in per_day_dict.items():
            result = result + key + ": {}".format(str(value).replace("'", "")[1:-1]) + "\n"
        return result

