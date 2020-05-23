from unittest import TestCase
from backend.general import get_first_sunday, get_last_saturday
from datetime import timedelta, date


class Test(TestCase):

    def test_get_date(self):
        month = 1
        year = 2020
        result = get_first_sunday(month, year)
        self.assertTrue(result == date(2020, month=1, day=5))
        result = get_last_saturday(month, year)
        self.assertTrue(result == date(2020, month=2, day=1))

        month = 12
        year = 2019
        result = get_first_sunday(month, year)
        self.assertTrue(result == date(2019, month=12, day=1))
        result = get_last_saturday(month, year)
        self.assertTrue(result == date(2020, month=1, day=4))


    def test_formatting(self):
        dd = date(2020, month=1, day=5)
        strin = dd.strftime("%-d.%m.%y")
        print(strin)