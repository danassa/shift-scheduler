import base64
import os
import pickle
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def email_shifts_to_volunteers(volunteers, url):
    credentials = get_email_credentials()
    service = build('gmail', 'v1', credentials=credentials)
    root_test = "<p dir='rtl'> פורסמו המשמרות לחודש הבא. ניתן למצוא את לוח המשמרות המלא כאן: {}<br><br>המשמרות שלך:<br>".format(url)
    message_text = root_test
    for name in volunteers.keys():
        volunteer = volunteers[name]
        for week in volunteer.assigned_slots:
            for slot in volunteer.assigned_slots[week][1]:
                message_text += "{}<br>".format(str(slot))
        message_text += "</p>"
        send_email(service, [volunteer.email_shifts_to_volunteers], "משמרות סהר", message_text)
        message_text = root_test


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


def get_email_credentials():
    credentials = None
    scope = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.compose']

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('resources/oauth_2_client_id.json', scope)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return credentials
