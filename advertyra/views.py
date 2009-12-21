import datetime, calendar
from django.utils import simplejson
from django.db.models import Count
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404

from advertyra.models import Advertisement, Campaign, Click
from advertyra.utils import clicks_for_ad

def adclick(request, ad_id):
    ad = get_object_or_404(Advertisement, pk=ad_id, visible=True)

    if ad.pk not in request.COOKIES:
        Click.objects.create(ad=ad)

        # Set a cookie
        response = HttpResponse()
        expires = datetime.datetime.strftime(datetime.datetime.utcnow().replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(str(ad.pk), 'clicked', expires=expires)
        
    print Click.objects.all().count()

    return HttpResponseRedirect(ad.link)

def user_is_staff(user):
    """ Check if a user has the staff status """
    return user.is_authenticated() and user.is_staff

@user_passes_test(user_is_staff)
def ad_click_by_month(request, ad_id, date):
    date = datetime.datetime.strptime(date, '%m-%Y')

    click_data = clicks_for_ad(ad_id, date)

    data = {'clicks': click_data['clicks'],
            'start_date': click_data['start'].strftime('%Y/%m/%d'),
            'end_date': click_data['end'].strftime('%Y/%m/%d') }
    
    return HttpResponse(simplejson.dumps(data),
                        mimetype='application/json')

@user_passes_test(user_is_staff)
def campaign_click_by_month(request, campaign_id, date):
    date = datetime.datetime.strptime(date, '%m-%Y')
    
    campaign = Campaign.objects.get(pk=campaign_id)
    
    campaign_data = {}
    for ad in campaign.ad.all():
        ad_data = {}
        clicks = clicks_for_ad(ad.pk)
        ad_data['data'] = clicks['clicks']
        ad_data['label'] = ad.title

        start_date = date.replace(day=1)
        end_date = start_date + datetime.timedelta(days=31)
        end_date.replace(day=1)

        ad_data['start'] = start_date.strftime('%Y/%m/%d')
        ad_data['end'] = end_date.strftime('%Y/%m/%d')

        campaign_data[ad.title] = ad_data

    return HttpResponse(simplejson.dumps(campaign_data),
                        mimetype='application/json')
