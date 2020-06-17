from src.backend.data import Data
from src.utils.hard_drive import restore_old_values
from src.frontend.events import start


if __name__ == "__main__":

    try:
        data = restore_old_values()
    except FileNotFoundError:
        data = Data()

    start(data)
