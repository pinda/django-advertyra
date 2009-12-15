from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth import User

from publisa.models import Publish

class Article(Publish):
    title = models.CharField(_('title'), max_length=124)
    slug = models.SlugField(_('slug'),
                            unique_for_month='publish',
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
    categories = models.ManyToManyField('Category', related_name='published')
