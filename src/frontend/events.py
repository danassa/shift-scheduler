import queue
from numbers import Number
import PySimpleGUI as sg
from gspread.exceptions import APIError
from src.utils.google_drive import update_schedule_sheet
from src.utils.hard_drive import save
from src.frontend.hebrew_popup import HebrewPopup
from src.backend.data import Data
from src.frontend.ui import initialize_windows, switch_week_window, update_window, update_details
from src.utils.constants import *


def start(data):
    sg.theme(THEME)
    gui_queue = queue.Queue()

    week_windows = initialize_windows(data)

    index = 0
    calendar_window = week_windows[index]
    calendar_window.un_hide()

    while True:
        try:
            events, values = calendar_window.read()
            if events is None or events == EXIT:
                response = sg.popup_yes_no(MSG_SAVE)
                if response == YES:
                    save(data)
                break
            elif events == MENU_SAVE:
                save(data)

            elif events == MENU_NEW:
                old_windows = week_windows
                data = Data()
                week_windows = initialize_windows(data)
                index = 0
                calendar_window = week_windows[index]
                calendar_window.un_hide()
                for window in old_windows:
                    window.close()

            elif events == MENU_UPDATE:
                data.update_requests_with_minimal_calendar_changes()
                save(data)
                HebrewPopup(MSG_SAVE_1, MSG_SAVE_2, non_blocking=False)
                break

            elif events == MENU_ASSIGN:
                data.auto_assignments()
                save(data)
                HebrewPopup(MSG_SAVE_1, MSG_SAVE_3, non_blocking=False)
                break

            elif events == B_NEXT:
                if index < len(week_windows)-1:
                    index = index + 1
                    calendar_window = switch_week_window(week_windows, data.volunteers, index, index - 1)
            elif events == B_PREV:
                if index > 0:
                    index = index - 1
                    calendar_window = switch_week_window(week_windows, data.volunteers, index, index + 1)

            elif events == MENU_UPLOAD:
                try:
                    values_to_publish, empty_slots = data.calendar.get_calender_values()
                    if empty_slots:
                        max_for_display = empty_slots[0:10]
                        response = sg.popup_yes_no(MSG_EMPTY_SLOTS, "\n".join(max_for_display), title=TITLE_EMPTY_SLOTS)
                        if response != YES:
                            continue
                    update_schedule_sheet(values_to_publish, data.calendar.first_date)
                    HebrewPopup(MSG_DONE, title=TITLE_DONE, non_blocking=False)
                    break
                except APIError as e:
                    HebrewPopup(MSG_FAIL, e.args[0]['message'], non_blocking=False)

            elif events == MENU_PUBLISH:
                try:
                    data.publish_shifts()
                    HebrewPopup(MSG_DONE, title=TITLE_DONE, non_blocking=False)
                    break
                except APIError as e:
                    HebrewPopup(MSG_FAIL, e.args[0]['message'], non_blocking=False)

            elif events == SEARCH:
                update_details(week_windows, data.volunteers[values[SEARCH]])
            else:
                parts = events.split("|")
                if parts[0] == NAME_TAG:
                    volunteer = data.volunteers[parts[1]]
                    HebrewPopup(volunteer.comments, volunteer.get_options_as_string(index + 1), volunteer.get_assignments_as_string(index + 1),
                                title=volunteer.name, font=FONT_12)
                else:
                    pick = values[events]
                    slot = data.calendar.find_slot_by_drop_down_string(parts)

                    if not isinstance(pick, Number):
                        volunteer = data.volunteers[pick]
                        volunteer.is_valid_assignment(slot, gui_queue)
                        changed_volunteers = slot.assign_volunteer(volunteer)
                    else:
                        changed_volunteers = slot.release_assignment()
                    for v in changed_volunteers:
                        data.volunteers[v.name] = v

                    update_window(calendar_window, changed_volunteers, index + 1, events, slot.get_value())

            try:
                response = gui_queue.get_nowait()
                HebrewPopup(response, title='')
            except queue.Empty:
                pass

        except UnicodeDecodeError:
            continue

    calendar_window.close()

