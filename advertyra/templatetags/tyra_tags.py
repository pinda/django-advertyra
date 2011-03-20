import re
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from advertyra.models import Advertisement
from advertyra.utils import render_placeholder

register = template.Library()

def do_placeholder(parser, token):
    error_string = '%r tag requires at least 1 argument' % token.split_contents()[0]
    try:
        # split_contents() knows not to split quoted strings.
        bits = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(error_string)
    if len(bits) == 2:
        return PlaceholderNode(bits[1])
    elif len(bits) == 3:
        return PlaceholderNode(bits[1], bits[2])
    elif len(bits) == 4:
        return PlaceholderNode(bits[1], bits[2], bits[3])
    else:
        raise template.TemplateSyntaxError(error_string)

class PlaceholderNode(template.Node):
    """This template node is used to output page content and
    is also used in the admin to dynamicaly generate input fields.

    eg: {% banner banner-name size template %}

    Keyword arguments:
    name -- the name of the placeholder
    """
    def __init__(self, name, size='100x100', template_name='advertyra/advertisement.html'):
        self.name = "".join(name.lower().split('"'))
        self.size = size
        self.template_name = template_name

    def render(self, context):
        if context.get('display_banner_names'):
            return "<!-- Banner: %s -->" % self.name

        return render_placeholder(self.name, context, self.size, self.template_name)

    def __repr__(self):
        return "<Banner: %s>" % self.name

register.tag('banner', do_placeholder)

@register.tag
def render_media(parser, token):
    """
    Gets form to put products in the cart

    Syntax::

        {% render_media for [object] [size] %}

    Example usage::

        {% render_media for product 500x500 %}

    """
    try:
        tag_name, for_name, obj, size = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, '%s is used as "{% render_form for <object> %}".' % token.content.split()[0]

    if for_name != "for": raise template.TemplateSyntaxError, 'Second argument must be "for"'
    return RenderMedia(obj, size)

class RenderMedia(template.Node):
    """ Render form for object """
    def __init__(self, obj, size):
        self.object = template.Variable(obj)
        self.size = template.Variable(size)

    def render(self, context):
        try:
            obj = self.object.resolve(context)
            size = self.size.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        else:
            width, height = size.split('x')
            t = template.loader.get_template('advertyra/includes/media_object.html')
            context = template.Context({'object': obj,
                                        'size': size,
                                        'width': width,
                                        'height': height,
                                        'MEDIA_URL': settings.MEDIA_URL })

            try:
                rendered = t.render(context)
            except template.TemplateSyntaxError:
                return ''
            else: return mark_safe(rendered)

class RandomAds(template.Node):
    def __init__(self, limit, var_name):
        self.limit = limit
        self.var_name = var_name

    def render(self, context):
        ad_list = Advertisement.objects.filter(visible=True)[:self.limit]
        if ad_list and (self.limit == 1):
            context[self.var_name] = ad_list[0]
        else:
            context[self.var_name] = ad_list

        return ''

@register.tag
def get_random_ads(parser, token):
    """
    Return a integer with the total number of profile updates

    Syntax::

        {% get_random_ad [limit] as [var_name] %}

    Example usage::

        {% get_random_ad 10 as ad_list %}

    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    limit, var_name = m.groups()
    return RandomAds(limit, var_name)
