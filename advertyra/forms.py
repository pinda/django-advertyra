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

    free_places = [[ad.pk, ad.title] for ad in Placeholder.objects.exclude(id__in=taken_places)]
    free_places.append(['', _('No place')])
    
    return free_places

class AdvertisementForm(forms.ModelForm):
    place = forms.ChoiceField(required=False)
    
    model = Advertisement

    def __init__(self, *args, **kwargs):
        super(AdvertisementForm, self).__init__(*args, **kwargs)

        place_list = get_free_places()
        if self.instance.place:
            place_list.append([self.instance.place.pk, self.instance.place.title])
            place_list.sort()
            
        self.fields['place'].choices = place_list
    
    def clean_place(self):
        if not self.cleaned_data['place']:
            return None
        return Placeholder.objects.get(pk=self.cleaned_data['place'])


class CampaignForm(forms.ModelForm):
    place = forms.ChoiceField(required=False)
    
    model = Campaign

    def __init__(self, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)

        place_list = get_free_places()
        if self.instance.place:
            place_list.append([self.instance.place.pk, self.instance.place.title])
            place_list.sort()
            
        self.fields['place'].choices = place_list

    def clean_place(self):
        if not self.cleaned_data['place']:
            return None
        return Placeholder.objects.get(pk=self.cleaned_data['place'])
    
                                               
