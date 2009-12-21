import datetime
from django import forms
from django.utils.translation import ugettext as _

from advertyra.models import Advertisement, Campaign

def placeholder_taken(placeholder):
    try:
        campaign = Campaign.objects.get(place=placeholder,
                                        start__lte=datetime.datetime.now(),
                                        end__gte=datetime.datetime.now())
    except Campaign.DoesNotExist:
        try:
            ad = Advertisement.objects.get(place=placeholder,
                                           visible=True)
        except Advertisement.DoesNotExist:
            return placeholder
        else:
            raise forms.ValidationError(_('Placeholder already taken by %s' % ad.title))
    else:
        raise forms.ValidationError(_('Placeholder already taken by %s' % campaign.title))

class AdvertisementForm(forms.ModelForm):
    model = Advertisement

    def clean_place(self):
        if self.cleaned_data['place']:
            return placeholder_taken(self.cleaned_data['place'])

class CampaignForm(forms.ModelForm):
    model = Campaign

    def clean_place(self):
        if self.cleaned_data['place']:
            return placeholder_taken(self.cleaned_data['place'])
                                               
