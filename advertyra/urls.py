from django.conf.urls.defaults import *

from advertyra import views as tyra_views

urlpatterns = patterns('',
   url(r'^click/(?P<ad_id>\d+)/$',
       tyra_views.adclick,
       name='adclick'),
)                      
    
