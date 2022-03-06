from datetime import datetime

from django.http import JsonResponse
from eventtimeline.models import TimelineEvent


def get_all_events(request):
    event_date = datetime.now()
    event_date = event_date.replace(year=event_date.year - 80)
    events = TimelineEvent.objects.filter(event_date__lte=event_date).order_by('event_date').to_list()
    return JsonResponse({'events': events, 'date': event_date}, safe=False)
