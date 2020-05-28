import queue
from numbers import Number
import PySimpleGUI as sg
from gspread.exceptions import APIError
from backend.general import *
from backend.google_drive import update_schedule_sheet
from backend.hard_drive import save
from backend.hebrew import HebrewPopup
from constants import *
from frontend.calendar import pull_data, initialize_windows, switch_week_window, update_window


def start():
    sg.theme(THEME)
    gui_queue = queue.Queue()

    dates, calendar, volunteers = pull_data()
    week_windows, calendar, volunteers = initialize_windows(dates, calendar, volunteers)

    index = 0
    calendar_window = week_windows[index]
    calendar_window.un_hide()

    while True:
        try:
            events, values = calendar_window.read()
            if events is None or events == EXIT:
                response = sg.popup_yes_no(MSG_SAVE)
                if response == YES:
                    save(calendar, volunteers)
                break
            elif events == MENU_SAVE:
                save(calendar, volunteers)

            elif events == MENU_NEW:
                old_windows = week_windows
                week_windows, calendar, volunteers = initialize_windows(*create_new_values())
                index = 0
                calendar_window = week_windows[index]
                calendar_window.un_hide()
                for window in old_windows:
                    window.close()

            elif events == MENU_UPDATE:
                calendar, volunteers = update_requests_with_minimal_calendar_changes(calendar, volunteers)
                save(calendar, volunteers)
                HebrewPopup(MSG_SAVE_1, MSG_SAVE_2, non_blocking=False)
                break

            elif events == B_NEXT:
                if index < len(week_windows)-1:
                    index = index + 1
                    calendar_window = switch_week_window(week_windows, volunteers, index, index - 1)
            elif events == B_PREV:
                if index > 0:
                    index = index - 1
                    calendar_window = switch_week_window(week_windows, volunteers, index, index + 1)

            elif events == MENU_CLOSE:
                try:
                    values_to_publish, empty_slots = get_calender_values(calendar, dates[FIRST_D], dates[LAST_D])
                    if empty_slots:
                        max_for_display = empty_slots[0:10]
                        response = sg.popup_yes_no(MSG_EMPTY_SLOTS, "\n".join(max_for_display), title=TITLE_EMPTY_SLOTS)
                        if response == YES:
                            update_schedule_sheet(values_to_publish, dates[FIRST_D])
                            #email_shifts_to_volunteers(volunteers, SHIFTS_LINK)
                            HebrewPopup(MSG_DONE, title=TITLE_DONE, non_blocking=False)
                            break
                except APIError as e:
                    HebrewPopup(MSG_FAIL, e.args[0]['message'], non_blocking=False)

            else:
                parts = events.split("|")
                if parts[0] == NAME_TAG:
                    volunteer = volunteers[parts[1]]
                    HebrewPopup(volunteer.get_options_as_string(index + 1), volunteer.get_assignments_as_string(index + 1),
                                title=volunteer.name, font=FONT_12)
                else:
                    pick = values[events]
                    slot = find_slot_by_drop_down_string(parts, calendar)

                    if not isinstance(pick, Number):
                        volunteer = volunteers[pick]
                        volunteer.is_valid_assignment(slot, gui_queue)
                        changed_volunteers = slot.assign_volunteer(volunteer)
                    else:
                        changed_volunteers = slot.release_assignment()
                    for v in changed_volunteers:
                        volunteers[v.name] = v

                    update_window(calendar_window, changed_volunteers, index + 1, events, slot.get_value())

            try:
                response = gui_queue.get_nowait()
                HebrewPopup(response, title='')
            except queue.Empty:
                pass

        except UnicodeDecodeError:
            continue

    calendar_window.close()


if __name__ == "__main__":
    start()
