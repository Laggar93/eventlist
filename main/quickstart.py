from __future__ import print_function
import datetime
import os.path
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': 'Тестовое событие',
        'location': 'Москва',
        'description': 'Описание события',
        'start': {
            'dateTime': '2025-10-17T09:00:00+03:00',
            'timeZone': 'Europe/Moscow',
        },
        'end': {
            'dateTime': '2025-10-17T10:00:00+03:00',
            'timeZone': 'Europe/Moscow',
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Событие создано: %s' % (event.get('htmlLink')))

if __name__ == '__main__':
    main()
