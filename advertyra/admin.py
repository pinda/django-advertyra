from django.contrib import admin

from advertyra.models import Campaign, Advertisement, Click
from advertyra.utils import get_placeholders

class ClickInline(admin.StackedInline):
    model = Click

class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', )
    inlines = [ClickInline, ]

    def add_view(self, request, form_url='', extra_context=None):
        get_placeholders(request)

        return super(AdvertisementAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, form_url='', extra_context=None):
        get_placeholders(request)

        return super(AdvertisementAdmin, self).change_view(request, form_url, extra_context)

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
    

    
