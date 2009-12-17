import os, re

from django.conf import settings
from django.template import loader
from django.template.context import RequestContext

from advertyra.models import Placeholder

PLACEHOLDERS = []

def get_placeholders(request):
    # Walk through all the templates which have a html extension
    for template_dir in settings.TEMPLATE_DIRS:
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                ext = file.split(".")[-1]
                if ext == "html":
                    PLACEHOLDERS.append(file)

    # Update context and get current_placeholders
    context = RequestContext(request)
    context.update({'request': request,
                    'display_banner_names': True })
    current_placeholders = [(p.title) for p in Placeholder.objects.all()]

    # For every template retrieve the placeholders and add to the DB
    for template in PLACEHOLDERS:
        temp = loader.get_template(template)
        temp_string = temp.render(context)

        placeholders = re.findall("<!-- Banner: (.+?) -->", temp_string)
        
        for placeholder in placeholders:
            try:
                Placeholder.objects.get(title__iexact=placeholder)
            except Placeholder.DoesNotExist:
                Placeholder.objects.create(title=placeholder)

    # Delete any non-existing placeholder
    removable = list(set(current_placeholders).difference(set(placeholders)))

    for placeholder in removable:
        Placeholder.objects.get(title__iexact=placeholder).delete()

def render_placeholder(placeholder_name, template=None):
    pass
