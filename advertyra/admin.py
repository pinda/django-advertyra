import datetime, calendar
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.db.models import Count

from advertyra.models import Campaign, Advertisement, Click
from advertyra.utils import get_placeholders

class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', )
    exclude = ('size', )

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

        for x in clicks:
            date = datetime.datetime.strptime(x['d'], '%m/%d/%Y')
            x['d'] = calendar.timegm(date.timetuple()) * 1000

        month_list = Click.objects.dates('datetime', 'month')
        clicks = [[x['d'], x['pk__count']] for x in clicks]
        
        extra_context = {'clicks': clicks, 'start_date': start_date, 'end_date': end_date, 'month_list': month_list }

        return super(AdvertisementAdmin, self).change_view(request, object_id, extra_context)

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', )

    def add_view(self, request, form_url='', extra_context=None):
        get_placeholders(request)

        return super(CampaignAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, form_url='', extra_context=None):
        get_placeholders(request)

        return super(CampaignAdmin, self).change_view(request, form_url, extra_context)

admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(Campaign, CampaignAdmin)
    

    
