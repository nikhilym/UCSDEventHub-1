from django.db import models
from django.utils import timezone
from datetime import datetime
import pytz
from hub.models import Event, UserProfile, OrganizationDetails, RSVP
from hub.models import Category
from django.db.models import Count
from django.db.models import Q

pst = pytz.timezone('US/Pacific')
# Hard coding PST as timezone as one time fix.
# Need to update this to get dynamic tz conversion

def is_user_attendee(user):
    if user.is_authenticated:
        return UserProfile.objects.filter(user=user).exists()

def search_events(search_text):
    today_date = datetime.now(pst).replace(hour=0, minute=0, second=0)
    event_results = []
    for keywords in search_text.split():
        event_results += Event.objects.filter((Q(title__icontains=keywords)|Q(location__icontains=keywords)|Q(hashtags__icontains=keywords)|Q(org__org_name__icontains=keywords)|Q(categories__category__icontains=keywords))&Q(start_date__gte=today_date)).all().values()
    event_results = list({v['id']:v for v in event_results}.values())
    event_results.sort(key = lambda item:item['start_date'])
    return event_results

def upcoming_events():
    today_date = datetime.now(pst).replace(hour=0, minute=0, second=0)
    events_results = list(Event.objects.filter(start_date__gte=today_date).all().values())
    events_results.sort(key = lambda item:(
        -get_rsvp_count(item['id']),item['start_date']))
    return events_results

def upcoming_events_by_org(orgid):
    today_date = datetime.now(pst).replace(hour=0, minute=0, second=0)
    events_results = list(Event.objects.filter(org_id=orgid).filter(start_date__gte=today_date).all().values())
    return events_results

def event_details(event_id):
    event = list(Event.objects.filter(id=event_id).all().values())
    event[0]["categories"] = list(Event.objects.filter(id=event_id).exclude(categories__isnull=True).all().values("categories__category"))
    return event

def add_event_to_db(event):
	event.save()

def check_user_name(username,is_org):
	if is_org:
		if(OrganizationDetails.objects.filter(user_name = username).exists()):
			return True
	else:
		if(UserProfile.objects.filter(user_name = username).exists()):
			return True
	return False

def user_event_rsvpd(user_id, event_id):
    rsvpd = RSVP.objects.filter(
        rsvp_user_id=user_id, rsvp_event_id=event_id).exists()
    return rsvpd

def save_rsvp(user_id, event_id):
    if not user_event_rsvpd(user_id, event_id):
        if UserProfile.objects.filter(user_id=user_id).exists() and \
            Event.objects.filter(id=event_id).exists():
            rsvp = RSVP()
            rsvp.rsvp_user_id = user_id
            rsvp.rsvp_event_id = event_id
            rsvp.save()

def remove_rsvp(user_id, event_id):
    if user_event_rsvpd(user_id, event_id):
        rsvp = RSVP.objects.filter(
            rsvp_user_id=user_id, rsvp_event_id=event_id)
        rsvp.delete()

def get_org_details(org_id):
    if OrganizationDetails.objects.filter(organization_id=org_id).exists():
        return OrganizationDetails.objects.get(organization_id=org_id)
    else:
        return None

def get_rsvp_events(user_id):
    user_events = RSVP.objects.filter(rsvp_user_id=user_id)
    events=[]
    for e in user_events:
        events += (Event.objects.filter(id=e.rsvp_event_id).all().values())
    return events

def get_rsvp_count(event_id):
    return RSVP.objects.filter(rsvp_event_id=event_id).values(
        'rsvp_event_id').count()

def get_organization_id(org_name):
    if OrganizationDetails.objects.filter(user_name=org_name).exists():
        return OrganizationDetails.objects.get(user_name=org_name).organization_id
    else:
        return None

def get_organization_name(org_id):
    return OrganizationDetails.objects.get(organization_id=org_id).org_name

def get_categories(id_list):
    return Category.objects.filter(id__in=id_list)