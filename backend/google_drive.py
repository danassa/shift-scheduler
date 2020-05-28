import gspread
from oauth2client.service_account import ServiceAccountCredentials
from constants import SCHEDULE_SPREADSHEET


def get_spreadsheet_from_drive(filename):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('resources/auth_service_account.json', scope)
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
    transposed = [[] for _ in range(max(len(row) for row in values))]
    for row in values:
        for x, res_row in zip(row, transposed):
            res_row.append(x)

    title = "{}/{}".format(first_date.month, first_date.year)
    spreadsheet.get_worksheet(0).duplicate(insert_sheet_index=0, new_sheet_name=title)
    spreadsheet.get_worksheet(0).update(transposed)
