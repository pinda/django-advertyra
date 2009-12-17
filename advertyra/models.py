from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

class Campaign(models.Model):
    title = models.CharField(_('title'), max_length=80)
    start = models.DateTimeField(_('start time'))
    end = models.DateTimeField(_('end time'))

    place = models.ForeignKey("Placeholder", blank=True, null=True)
    ad = models.ManyToManyField("Advertisement")

    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')

    def __unicode__(self):
        return self.title

class Advertisement(models.Model):
    title = models.CharField(_('title'), max_length=80)
    link = models.URLField(_('link'), blank=True, null=True)
    ad = models.ImageField(_('advertisement'), upload_to='advertyra/')
    visible = models.BooleanField(_('visible'), default=True)

    place = models.ForeignKey("Placeholder", blank=True, null=True)
    
    class Meta:
        verbose_name = _('Advertisement')
        verbose_name_plural = _('Advertisements')

    def __unicode__(self):
        return self.title

class Click(models.Model):
    ipadress = models.IPAddressField(_('ip address'))
    datetime = models.DateTimeField(_('date'), auto_now_add=True)

    ad = models.ForeignKey(Advertisement, related_name='ads')

    def __unicode__(self):
        return self.ad

class Placeholder(models.Model):
    title = models.CharField(_('title'), max_length=80)

    def __unicode__(self):
        return self.title

    
