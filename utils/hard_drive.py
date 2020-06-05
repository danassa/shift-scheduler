import dill
from utils.constants import VOLUNTEERS_FILE


def save(volunteers):
    with open(VOLUNTEERS_FILE, "wb") as dill_file:
        dill.dump(volunteers, dill_file)


def restore_old_values():
    with open(VOLUNTEERS_FILE, "rb") as dill_file:
        volunteers = dill.load(dill_file)

    return volunteers
