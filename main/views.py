import datetime
from django.shortcuts import render
from django.http import HttpResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from eventlist import config

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def add_event_to_calendar(request):
    service = get_calendar_service()
    calendar_list = service.calendarList().list().execute()

    for calendar_entry in calendar_list['items']:
        print(calendar_entry['summary'], "→", calendar_entry['id'])
    try:
        date_str = request.GET.get('date', '')
        time_str = request.GET.get('time', '')
        guide = request.GET.get('guide', '')
        tour_type = request.GET.get('tour_type', '')
        customer = request.GET.get('customer', '')
        phone = request.GET.get('phone', '')
        email = request.GET.get('email', '')
        payment = request.GET.get('payment', '')
        event_type = request.GET.get('event_type', '')
        comments = request.GET.get('comments', '')
        mail_list = request.GET.get('mail', '')

        if not date_str or not time_str:
            return HttpResponse("Ошибка: отсутствуют дата или время", status=400)

        try:
            date_obj = datetime.datetime.strptime(date_str, '%d.%m.%Y')
            time_obj = datetime.datetime.strptime(time_str, '%H:%M')
        except ValueError:
            return HttpResponse("Ошибка: неверный формат даты или времени", status=400)

        start_datetime = datetime.datetime.combine(date_obj.date(), time_obj.time())
        end_datetime = start_datetime + datetime.timedelta(hours=1)

        start_iso = start_datetime.strftime('%Y-%m-%dT%H:%M:%S+03:00')
        end_iso = end_datetime.strftime('%Y-%m-%dT%H:%M:%S+03:00')

        description_parts = []
        if guide and guide != "Нет гида":
            description_parts.append(f"Гид: {guide}")
        if tour_type:
            description_parts.append(f"Вид экскурсии: {tour_type}")
        if customer:
            description_parts.append(f"Заказчик: {customer}")
        if phone:
            description_parts.append(f"Контактный номер: {phone}")
        if email:
            description_parts.append(f"Почта: {email}")
        if payment:
            description_parts.append(f"Оплата: {payment}")
        if event_type:
            description_parts.append(f"Тип: {event_type}")
        if comments:
            description_parts.append(f"Комментарии: {comments}")

        description = "\n".join(description_parts)

        attendees = []

        if email:
            attendees.append({'email': email.strip()})

        if mail_list:
            for addr in mail_list.split(','):
                addr = addr.strip()
                if addr:
                    attendees.append({'email': addr})

        event = {
            'summary': f'{tour_type} - {guide}' if guide and guide != "Нет гида" else tour_type,
            'location': 'Москва',
            'description': description,
            'start': {
                'dateTime': start_iso,
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': end_iso,
                'timeZone': 'Europe/Moscow',
            },
            'attendees': attendees,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }

        event = service.events().insert(
            calendarId=config.calendar_id,
            body=event,
            sendUpdates='all'
        ).execute()

        return HttpResponse(
            f"Событие успешно добавлено в календарь!<br>"
            f"Ссылка: <a href='{event.get('htmlLink')}'>{event.get('htmlLink')}</a>"
        )

    except HttpError as error:
        return HttpResponse(f"Ошибка Google Calendar: {error}", status=500)
    except Exception as e:
        return HttpResponse(f"Произошла ошибка: {e}", status=500)




def main_page_view(request):

    content = {
    }

    return render(request, 'index.html', content)
