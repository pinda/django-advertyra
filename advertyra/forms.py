import datetime
from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from advertyra.models import Advertisement, Campaign, Placeholder

def get_free_places(campaign=False):
    """ Determine which placeholders are currently available """
    ad_places = Advertisement.objects.filter(place__isnull=False).values("place__pk")
    cam_places = Campaign.objects.filter(place__isnull=False).values("place__pk")

    taken_places = set()
    for ad in ad_places:
        taken_places.add(ad['place__pk'])
    for ad in cam_places:
        taken_places.add(ad['place__pk'])

    places = Placeholder.objects.exclude(id__in=taken_places)

    # For campaign all places are possible
    if campaign:
        taken_places = []

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

        self.fields['ad'].help_text = getattr(settings, 'ADVERTYRA_HELP_TEXT', '')

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

        place_list = get_free_places(campaign=True)
        if self.instance.place and not self.instance.place.pk in [x[0] for x in place_list]:
            place_list.append([self.instance.place.pk, self.instance.place.title])
            place_list.sort()

        self.fields['place'].choices = place_list

    def clean_place(self):
        if not self.cleaned_data['place']:
            return None
        return Placeholder.objects.get(pk=self.cleaned_data['place'])

    def clean(self):
        """
        If placeholder is currently occupied
        start date must be later then his end date

        """
        # Check for advertisements
        try:
            Advertisement.objects.get(place=self.cleaned_data['place'],
                                      end__gt=self.cleaned_data['start']).exclude(pk=self.instance.pk)
        except:
            pass
        else:
            raise forms.ValidationError(_('Place is not available at %(date)s' % \
                                          {'date': self.cleaned_data['start'].strftime('%d-%m-%Y %H:%M') }))

        # Check for campaigns
        try:
            Campaign.objects.get(place=self.cleaned_data['place'],
                                 end__gt=self.cleaned_data['start']).exlude(pk=self.instance.pk)
        except:
            pass
        else:
            raise forms.ValidationError(_('Place is not available at %(date)s' % \
                                          {'date': self.cleaned_data['start'].strftime('%d-%m-%Y %H:%M') }))

        return self.cleaned_data
