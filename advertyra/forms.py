import datetime
from django import forms
from django.utils.translation import ugettext as _

from advertyra.models import Advertisement, Campaign, Placeholder

def get_free_places():
    """ Determine which placeholders are currently available """
    ad_places = Advertisement.objects.filter(place__isnull=False).values("place__pk")
    cam_places = Campaign.objects.filter(place__isnull=False).values("place__pk")

    taken_places = []
    for ad in ad_places:
        taken_places.append(ad['place__pk'])
    for ad in cam_places:
        taken_places.append(ad['place__pk'])

    places = Placeholder.objects.exclude(id__in=taken_places)

    if places:
        free_places = [[ad.pk, ad.title] for ad in Placeholder.objects.exclude(id__in=taken_places)]
        return free_places
    else:
        return (('0', _('No places available')),)

class AdvertisementForm(forms.ModelForm):
    place = forms.ChoiceField()
    
    model = Advertisement

    def __init__(self, *args, **kwargs):
        super(AdvertisementForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = get_free_places()
    
    def clean_place(self):
        if self.cleaned_data['place'] == "0":
            raise forms.ValidationError(_('There are no free places, create one first'))
        return Placeholder.objects.get(pk=self.cleaned_data['place'])


class CampaignForm(forms.ModelForm):
    place = forms.ChoiceField()
    
    model = Campaign

    def __init__(self, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = get_free_places()

    def clean_place(self):
        if self.cleaned_data['place'] == "0":
            raise forms.ValidationError(_('There are no free places, create one first'))
        return Placeholder.objects.get(pk=self.cleaned_data['place'])
    
                                               
