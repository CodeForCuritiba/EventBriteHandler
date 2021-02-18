import os

from datetime import date
from functools import reduce
from pprint import PrettyPrinter

from eventbrite import Eventbrite
import telebot


def get_info_from_eventbrite(only_today=True):
    token_id = os.environ.get('TOKEN_ID', None)
    event_id = os.environ.get('EVENT_ID', None)

    if token_id is None or event_id is None:
        print('Env var TOKEN_ID and EVENT_ID must be set before running this app.')
        exit(1)

    evtb = Eventbrite(token_id)

    print(" -> Getting information about the event...")
    event = evtb.get_event(id=event_id, expand='ticket_classes')

    since = date.today().strftime("%Y-%m-%dT%H:%M:%SZ") if only_today else None

    print(f" -> Fetching attendees since {since}")
    attendee_list = evtb.get_event_attendees(event_id=event_id, status='attending', changed_since=since)

    ticket_list = [{
        'name': item['name'],
        'total': item['quantity_total'],
        'sold': item['quantity_sold']
    } for item in event['ticket_classes']]

    summary = {
        'total_sold': reduce(lambda x, y: x['sold'] + y['sold'], ticket_list),
        'grand_total': reduce(lambda x, y: x['total'] + y['total'], ticket_list),
        'details': ticket_list,
        'attendee_summary': {
            'object_count': attendee_list['pagination']['object_count'],
            'has_more_items': attendee_list['pagination']['has_more_items']
        },
        'attendee_list_since': since,
        'latest_attendee_list': [
            {
                'name': a['profile']['name'],
                'company': a['profile']['company'],
                'ticket_type': a['ticket_class_name'],
                'status': a['status']
            } for a in attendee_list['attendees']
        ]
    }

    return summary


def report_to_telegram(chat_id=None, report=None):
    telegram_token = os.environ.get('TELEGRAM_TOKEN_ID', None)
    telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID', None)

    event_day = date(month=3, day=6, year=2021)
    today = date.today()

    days_left = event_day - today

    msg_days_left = ''
    attendees_msg = ''

    if days_left.days >= 1:
        msg_days_left = f"🔥 Faltam <b>{days_left.days}</b> dia(s) para o evento!\n\n"
        attendees_msg = f"📈 Ultimos cadastros de hoje: <b>{report['attendee_summary']['object_count']}</b>\n<pre>"

        for detail in report['latest_attendee_list']:
            attendees_msg += f"- {detail['name']} - {detail['company']}\n" \

        attendees_msg += '</pre>\n'

        if report['attendee_summary']['has_more_items']:
            attendees_msg += "E <b>muitos outros</b>!"

    bot = telebot.TeleBot(token=telegram_token, parse_mode='HTML')

    message = f"📰 Boletim do evento OpenData Day 2021!\n\n{msg_days_left}" \
              f"🔩 <b>Até agora vendemos {report['total_sold']} Ingresso(s)</b> \n{attendees_msg}"

    bot.send_message(chat_id=telegram_chat_id, text=message)
    print('Message sent to Telegram!')

    return bot.get_updates()


def main():
    pp = PrettyPrinter()

    print("Code for Curitiba - EventBrite connector")

    print(" -> Summary")
    event_summary = get_info_from_eventbrite()
    pp.pprint(event_summary)

    print(" -> Telegram report")

    updates = report_to_telegram(report=event_summary)
    for item in updates:
        pp.pprint(item)

    print("Done")


if __name__ == '__main__':
    main()
