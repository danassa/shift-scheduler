import base64
import os
import pickle
from email.mime.text import MIMEText
import gspread
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def get_email_credentials():
    creds = None
    scope = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.compose']

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('resources/oauth_2_client_id.json', scope)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def send_email(service, addresses, subject, message_text):
    message = MIMEText(message_text, 'html')
    message['to'] = ",".join(addresses)
    message['from'] = "sahar-service-account@sahar-schedule.iam.gserviceaccount.com"
    message['subject'] = subject

    encoded_message = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    try:
        service.users().messages().send(userId="me", body=encoded_message).execute()
    except HttpError as error:
        print('An error occurred: %s' % error)


def get_sheets_from_drive(filename):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('resources/auth_service_account.json', scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open(filename)
    print("spreadsheet")
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


def update_schedule_sheet(ss, values, first_date):
    transposed = [[] for _ in range(max(len(row) for row in values))]
    for row in values:
        for x, res_row in zip(row, transposed):
            res_row.append(x)

    title = "{}/{}".format(first_date.month, first_date.year)
    ss.get_worksheet(0).duplicate(insert_sheet_index=0, new_sheet_name=title)
    ss.get_worksheet(0).update(transposed)
