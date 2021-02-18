import os
from functools import reduce
from pprint import PrettyPrinter
from eventbrite import Eventbrite


def main(token_id, event_id):

    pp = PrettyPrinter()

    print("Code for Curitiba - EventBrite conenctor")
    evtb = Eventbrite(token_id)

    print(" -> Getting information about the event...")
    event = evtb.get_event(id=event_id, expand='ticket_classes')

    attendee_list = evtb.get_event_attendees(event_id=event_id, status='attending')

    ticket_list = [{
        'name': item['name'],
        'total': item['quantity_total'],
        'sold': item['quantity_sold']
    } for item in event['ticket_classes']]

    summary = {
        'total_sold': reduce(lambda x, y: x['sold'] + y['sold'], ticket_list),
        'grand_total': reduce(lambda x, y: x['total'] + y['total'], ticket_list),
        'details': ticket_list
    }

    pp.pprint(summary)
    pp.pprint(attendee_list)


if __name__ == '__main__':
    token_id = os.environ.get('TOKEN_ID', None)
    event_id = os.environ.get('EVENT_ID', None)

    if token_id is None or event_id is None:
        print('Env var TOKEN_ID and EVENT_ID must be set before running this app.')
        exit(1)

    main(token_id, event_id)
