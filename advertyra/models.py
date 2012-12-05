import datetime, os
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

IMAGE_FILE_TYPES = ('jpg', 'png', 'jpeg')
GIF_FILE_TYPES = ('gif',)
FLASH_FILE_TYPES = ('flv', 'swf')

class Campaign(models.Model):
    title = models.CharField(_('title'), max_length=80)
    start = models.DateTimeField(_('start time'), default=datetime.datetime.now())
    end = models.DateTimeField(_('end time'), blank=True, null=True)

    place = models.ForeignKey("Placeholder", blank=True, null=True)
    ad = models.ManyToManyField("Advertisement")

    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        ordering = ['start', 'end']

    def __unicode__(self):
        return self.title

class Advertisement(models.Model):
    title = models.CharField(_('title'), max_length=80)
    link = models.URLField(_('link'), blank=True, null=True)
    ad = models.FileField(_('advertisement'), upload_to='tyra/')
    visible = models.BooleanField(_('visible'), default=True)
    extra = models.TextField(_('extra'), blank=True, null=True, help_text=_('optional text to display in your templates'))

    place = models.ForeignKey("Placeholder", blank=True, null=True)

    class Meta:
        verbose_name = _('Advertisement')
        verbose_name_plural = _('Advertisements')
        ordering = ['title',]

    def __unicode__(self):
        return self.title

    @property
    def media_type(self):
        file_type = self.ad.url.split('.')[-1]
        if file_type in IMAGE_FILE_TYPES:
            return 'image'
        elif file_type in GIF_FILE_TYPES:
            return 'gif'
        elif file_type in FLASH_FILE_TYPES:
            return 'flash'

class Click(models.Model):
    datetime = models.DateTimeField(_('date'), auto_now_add=True)

    ad = models.ForeignKey(Advertisement, related_name='clicks')

    def __unicode__(self):
        return '%s' % self.ad.title

class Placeholder(models.Model):
    title = models.CharField(_('title'), max_length=80)

    def __unicode__(self):
        return self.title



