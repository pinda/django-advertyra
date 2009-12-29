import datetime
from django import forms
from django.utils.translation import ugettext as _

from advertyra.models import Advertisement, Campaign

def placeholder_taken(placeholder, ad_pk=None, cam_pk=None):
    try:
        campaign = Campaign.objects.exclude(pk=cam_pk).get(place=placeholder,
                                        start__lte=datetime.datetime.now(),
                                        end__gte=datetime.datetime.now())
    except Campaign.DoesNotExist:
        try:
            ad = Advertisement.objects.exclude(pk=ad_pk).get(place=placeholder,
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
        try:
            current_ad = Advertisement.objects.get(title__iexact=self.cleaned_data['title'])
        except Advertisement.DoesNotExist:
            return self.cleaned_data['place']
        
        if self.cleaned_data['place']:
            return placeholder_taken(self.cleaned_data['place'], ad_pk=current_ad.pk)

class CampaignForm(forms.ModelForm):
    model = Campaign

    def clean_place(self):
        try:
            current_cam = Campaign.objects.get(title__iexact=self.cleaned_data['title'])
        except Campaign.DoesNotExist:
            return self.cleaned_data['place']
        
        if self.cleaned_data['place']:
            return placeholder_taken(self.cleaned_data['place'], current_cam.pk)
                                               
