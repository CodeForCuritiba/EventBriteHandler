import os

from datetime import date
from functools import reduce
from pprint import PrettyPrinter

from eventbrite import Eventbrite


def get_info(token_id, event_id, only_today=True):
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


def main(token_id, event_id):
    print("Code for Curitiba - EventBrite conenctor")
    event_summary = get_info(token_id, event_id)

    pp = PrettyPrinter()
    pp.pprint(event_summary)


if __name__ == '__main__':
    token_id = os.environ.get('TOKEN_ID', None)
    event_id = os.environ.get('EVENT_ID', None)

    if token_id is None or event_id is None:
        print('Env var TOKEN_ID and EVENT_ID must be set before running this app.')
        exit(1)

    main(token_id, event_id)
