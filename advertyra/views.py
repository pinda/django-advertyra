import datetime, calendar
from django.utils import simplejson
from django.db.models import Count
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404

from advertyra.models import Advertisement, Click

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

    start_date = date.replace(day=1)
    end_date = start_date + datetime.timedelta(days=31)
    end_date.replace(day=1)

    # select clicks for this ad grouped by day
    select_data = {"d": """strftime('%%m/%%d/%%Y', datetime)"""}
    clicks = Click.objects.filter(ad__pk=ad_id,
                                  datetime__gte=start_date,
                                  datetime__lte=end_date).extra(select=select_data).values('d').annotate(Count("pk")).order_by()

    for x in clicks:
        date = datetime.datetime.strptime(x['d'], '%m/%d/%Y')
        x['d'] = calendar.timegm(date.timetuple()) * 1000

    month_list = Click.objects.dates('datetime', 'month')
    clicks = [[x['d'], x['pk__count']] for x in clicks]

    data = {'clicks': clicks,
            'start_date': start_date.strftime('%Y/%m/%d'),
            'end_date': end_date.strftime('%Y/%m/%d') }
    
    return HttpResponse(simplejson.dumps(data),
                        mimetype='application/json')

