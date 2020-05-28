import dill

from constants import META_FILE, FIRST_D, LAST_D, CALENDAR_FILE, VOLUNTEERS_FILE


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