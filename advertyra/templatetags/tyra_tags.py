from django import template

from advertyra.utils import render_placeholder

register = template.Library()

def do_placeholder(parser, token):
    error_string = '%r tag accepts only 1 argument' % token.contents[0]
    try:
        # split_contents() knows not to split quoted strings.
        tag, name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(error_string)
    if not name:
        raise template.TemplateSyntaxError(error_string)
    else:
        return PlaceholderNode(name)
 
class PlaceholderNode(template.Node):
    """This template node is used to output page content and
    is also used in the admin to dynamicaly generate input fields.
    
    eg: {% banner banner-name %}
    
    Keyword arguments:
    name -- the name of the placeholder
    """
    def __init__(self, name):
        self.name = "".join(name.lower().split('"'))
 
    def render(self, context):
        if context.get('display_banner_names'):
            return "<!-- Banner: %s -->" % self.name
        
        if not 'request' in context:
            return ''

        return render_placeholder(self.name)
    
    def __repr__(self):
        return "<Banner: %s>" % self.name

register.tag('banner', do_placeholder)
