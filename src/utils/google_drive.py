import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.utils.constants import SCHEDULE_SPREADSHEET, AUTH_SERVICE
import re


def get_spreadsheet_from_drive(filename):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(AUTH_SERVICE, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open(filename)
    return spreadsheet


def get_sheet(spreadsheet, sheet_name):
    sheet = spreadsheet.worksheet(sheet_name)
    return sheet


def get_header(sheet):
    header = sheet.row_values(1)
    return header


def get_data(sheet):
    data = sheet.get_all_records()
    return data


def get_column(sheet, index):
    values = sheet.col_values(index)
    return values


def update_schedule_sheet(values, first_date):
    spreadsheet = get_spreadsheet_from_drive(SCHEDULE_SPREADSHEET)
    max_elements = max(len(row) for row in values)
    result = []
    for i in range(0, max_elements):
        res_row = []
        for row in values:
            try:
                field = row[i]
            except:
                field = ""
            res_row.append(field)
        result.append(res_row)

    title = "{}/{}".format(first_date.month, first_date.year)
    new_sheet = get_sheet(spreadsheet, "Format").duplicate(insert_sheet_index=0, new_sheet_name=title)
    new_sheet.update(result)

    hours_cells = new_sheet.findall(re.compile(r'\d\d-\d\d'))
    for cell in hours_cells:
        new_sheet.format(cell.address, {"backgroundColor": {
                "red": 	0.835,
                "green": 0.6509,
                "blue": 0.741
            }})
