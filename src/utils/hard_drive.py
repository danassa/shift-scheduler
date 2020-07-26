import dill
from src.utils.constants import DATA_FILE


def save(data):
    with open(DATA_FILE, "wb") as dill_file:
        dill.dump(data, dill_file)


def restore_old_values():
    with open(DATA_FILE, "rb") as dill_file:
        volunteers = dill.load(dill_file)

    return volunteers
