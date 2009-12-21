import datetime, calendar, itertools
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.db.models import Count

from advertyra.models import Campaign, Advertisement, Click
from advertyra.forms import AdvertisementForm, CampaignForm
from advertyra.utils import get_placeholders

def mktimetuple(day, date):
    date = datetime.date(date.year, date.month, day)
    return calendar.timegm(date.timetuple()) * 1000

def click_count(value):
    if not value == 0:
        return value['pk__count']
    else:
        return value

class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'place', 'visible' )
    list_filter = ('visible', )
    exclude = ('size', )
    form = AdvertisementForm

    class Media:
        js = ('http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js',
              'advertyra/js/jquery.flot.min.js')

    def add_view(self, request, form_url='', extra_context=None):
        get_placeholders(request)

        return super(AdvertisementAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, extra_context=None):
        get_placeholders(request)

        # Determine start and end date
        start_date = datetime.datetime.now().date().replace(day=1)
        end_date = start_date + datetime.timedelta(days=31)
        end_date.replace(day=1)

        # select clicks for this ad grouped by day
        select_data = {"d": """strftime('%%m/%%d/%%Y', datetime)"""}
        clicks = Click.objects.filter(ad__pk=object_id,
                                      datetime__gte=start_date,
                                      datetime__lte=end_date).extra(select=select_data).values('d').annotate(Count("pk")).order_by()

        c = calendar.Calendar(calendar.SUNDAY)

        by_day = dict([
                (dom, list(items)[0])
                for dom, items in itertools.groupby(clicks, lambda c: c['d'].split('/')[1])
        ])

        days = dict([[day, by_day.get(str(day), 0)] for day in c.itermonthdays(start_date.year, start_date.month)
                     if day != 0
                     and day <= datetime.datetime.now().day
                     and start_date.month == datetime.datetime.now().month
                     ])
        
        clicks = [[mktimetuple(day[0], start_date), click_count(day[1])] for day in days.items()]

        month_list = Click.objects.dates('datetime', 'month')

        extra_context = {'clicks': clicks, 'start_date': start_date, 'end_date': end_date, 'month_list': month_list }

        return super(AdvertisementAdmin, self).change_view(request, object_id, extra_context)

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end')
    list_filter = ('ad', )
    form = CampaignForm
    
    def add_view(self, request, form_url='', extra_context=None):
        get_placeholders(request)

        return super(CampaignAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, form_url='', extra_context=None):
        get_placeholders(request)

        return super(CampaignAdmin, self).change_view(request, form_url, extra_context)

admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(Campaign, CampaignAdmin)
    

    
