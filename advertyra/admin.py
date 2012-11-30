import datetime
from django.contrib import admin
from django.shortcuts import get_object_or_404

from advertyra.models import Campaign, Advertisement, Click, Placeholder
from advertyra.forms import AdvertisementForm, CampaignForm
from advertyra.utils import get_placeholders, clicks_for_ad

class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'place', 'visible' )
    list_filter = ('visible', )
    form = AdvertisementForm

    class Media:
        js = ('http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js',
              'advertyra/js/jquery.flot.min.js',
              'advertyra/js/advertyra.plot.js')

        css = {'all': ('advertyra/css/advertyra.css',) }

    def add_view(self, request, form_url='', extra_context=None):
        get_placeholders(request)

        return super(AdvertisementAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url = '', extra_context=None):
        get_placeholders(request)

        click_data = clicks_for_ad(object_id)

        month_list = Click.objects.filter(ad__pk=object_id).dates('datetime', 'month')

        extra_context = {'clicks': click_data['clicks'], 'start_date': click_data['start'], 'end_date': click_data['end'], 'month_list': month_list }

        return super(AdvertisementAdmin, self).change_view(request, object_id, form_url, extra_context)

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'place', 'start', 'end')
    list_filter = ('ad', 'start')
    form = CampaignForm

    class Media:
        js = ('http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js',
              'advertyra/js/jquery.flot.min.js',
              'advertyra/js/advertyra.plot.js')

        css = {'all': ('advertyra/css/advertyra.css',) }

    def add_view(self, request, form_url='', extra_context=None):
        get_placeholders(request)

        return super(CampaignAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        get_placeholders(request)

        # Determine start and end date
        start_date = datetime.datetime.now().date().replace(day=1)
        end_date = start_date + datetime.timedelta(days=31)
        end_date.replace(day=1)

        campaign = Campaign.objects.get(pk=object_id)
        month_list = Click.objects.filter(ad__pk__in=campaign.ad.all()).dates('datetime', 'month')

        extra_context = {'month_list': month_list,
                         'start_date': start_date,
                         'end_date': end_date }

        return super(CampaignAdmin, self).change_view(request, object_id, form_url, extra_context)

admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(Campaign, CampaignAdmin)
#admin.site.register(Placeholder)
