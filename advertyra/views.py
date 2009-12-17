import datetime
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
