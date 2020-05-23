from math import floor


class Slot:

    def __init__(self, date, time, role, person, day):
        self.date = date
        self.time = time
        self.person = person
        self.assignment = []
        self.options = []
        self.role = role
        self.week = self.calculate_week(day)

    def add_volunteer(self, volunteer):
        if volunteer not in self.options:
            self.options.append(volunteer)

    def search_optional_volunteer(self, name):
        for v in self.options:
            if v.name == name:
                return v
        return None

    def get_names(self):
        names = [len(self.options)]
        for volunteer in self.options:
            names.append(volunteer.name)
        return names

    def get_value(self):
        if len(self.assignment) == 0:
            return len(self.options)
        elif len(self.assignment) == 1:
            return self.assignment[0].name
        else:
            return "{}/{}".format(self.assignment[0].name, self.assignment[1].name)

    def assign_volunteer(self, volunteer):
        updated_volunteers = [volunteer]
        if len(self.assignment) == 0:
            self.assignment.append(volunteer)
        elif len(self.assignment) == 1:
            if self.assignment[0].privileged or volunteer.privileged:
                self.assignment.append(volunteer)
            else:
                updated_volunteers.append(self.assignment[0])
                self.assignment[0].remove_slot(self)
                self.assignment = [volunteer]
        else:
            for v in self.assignment:
                v.remove_slot(self)
                updated_volunteers.append(v)
            self.assignment = [volunteer]

        volunteer.assign_slot(self)
        return updated_volunteers

    @staticmethod
    def calculate_week(day):
        week = floor(day / 7)
        return week + 1

    def is_assignment_valid(self):
        for assigned in self.assignment:
            result = self.search_optional_volunteer(assigned.name)
            if result is None:
                return False
        return True

    def release_assignment(self):
        released = self.assignment
        for v in self.assignment:
            v.remove_slot(self)
        self.assignment = []
        return released

    def is_drop_down_repr(self, values):
        return values[1] == self.time and values[2] == self.role and int(values[3]) == self.person

    def __str__(self):
        return "{} {}".format(self.date.strftime("%-d.%-m.%Y"), self.time)
