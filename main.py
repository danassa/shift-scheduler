from backend.data import Data
from utils.hard_drive import restore_old_values
from frontend.events import start


if __name__ == "__main__":

    try:
        data = restore_old_values()
    except:
        data = Data()

    start(data)
