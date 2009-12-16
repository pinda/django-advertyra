from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

import publisa

class Article(publisa.models.Status):
    title = models.CharField(_('title'), max_length=124)
    slug = models.SlugField(_('slug'),
                            help_text=_('Used to create the URL for this article.'))
    author = models.ForeignKey(User, verbose_name=_('Author'))
    teaser = models.TextField(_('teaser'),
                              blank=True,
                              help_text=_('If left blank, the entire post will \
                                          be shown on the frontpage.'))
    body = models.TextField(_('body'))
    allow_comments = models.BooleanField(_('allow comments'),
                                         default=True,)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    @models.permalink
    def get_absolute_url(self):
        return ('artikelly-detail', (), {
            'year': self.publish.publish.year,
            'month': self.publish.publish.strftime('%b').lower(),
            'day': self.publish.publish.day,
            'slug': self.slug })

    def __unicode__(self):
        return '%(title)s' % {'title': self.title}

publisa.register(Article, allow_banners=False)
