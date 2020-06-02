import dill

from constants import VOLUNTEERS_FILE


def save(volunteers):
    with open(VOLUNTEERS_FILE, "wb") as dill_file:
        dill.dump(volunteers, dill_file)


def restore_old_values():
    # with open(META_FILE, "rb") as dill_file:
    #     dates = dill.load(dill_file)
    # with open(CALENDAR_FILE, "rb") as dill_file:
    #     calendar = dill.load(dill_file)
    with open(VOLUNTEERS_FILE, "rb") as dill_file:
        volunteers = dill.load(dill_file)

    return volunteers
