import os, re, datetime, calendar, itertools

from django.conf import settings
from django.db.models import Count, Q
from django.template import loader
from django.template.context import RequestContext

from advertyra.models import Campaign, Advertisement, Placeholder, Click

def get_placeholders(request):
    # Walk through all the templates which have a html extension
    placeholders = []
    for template_dir in settings.TEMPLATE_DIRS:
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                ext = file.split(".")[-1]
                if ext == "html":
                    placeholders.append(os.path.join(root, file))

    # Update context and get current_placeholders
    context = RequestContext(request)
    context.update({'request': request,
                    'display_banner_names': True })
    current_placeholders = [(p.title) for p in Placeholder.objects.all()]

    # For every template retrieve the placeholders and add to the DB
    all_positions = []
    for template in placeholders:
        file = open(template, 'r')
        temp_string = file.read()
        banner_re = r'{% banner (?P<title>[-\w]+).*%}'

        for match in re.finditer(banner_re, temp_string):
            title = match.group('title')
            all_positions.append(title)
            try:
                Placeholder.objects.get(title__iexact=title)
            except Placeholder.DoesNotExist:
                Placeholder.objects.create(title=title)

    # Delete any non-existing placeholder
    removable = list(set(current_placeholders).difference(set(all_positions)))

    for placeholder in removable:
        Placeholder.objects.get(title__iexact=placeholder).delete()

def render_placeholder(placeholder_name, context, size, template):
    try:
        campaign = Campaign.objects.get(Q(place__title__iexact=placeholder_name,
                                        start__lte=datetime.datetime.now()),
                                        Q(end__gte=datetime.datetime.now())| Q(end=None)
                                        )
        ads = campaign.ad.all()
    except Campaign.DoesNotExist:
        try:
            ad = Advertisement.objects.get(place__title__iexact=placeholder_name, visible=True)
        except Advertisement.DoesNotExist:
            return ''
        else:
            ads = [ad, ]

    context.update({'ads': ads,
                    'size': size })

    template = loader.get_template(template)
    template = template.render(context)

    return template

def mktimetuple(day, date):
    date = datetime.date(date.year, date.month, day)
    return float(calendar.timegm(date.timetuple()) * 1000)

def click_count(value):
    if not value == 0:
        return value['pk__count']
    else:
        return value

def clicks_for_ad(pk, start_date=datetime.datetime.now()):
    """
    Return all the clicks for this ad by month
    Returns click count, start and end date
    """
    # Determine start and end date
    start_date = start_date.date().replace(day=1)
    end_date = start_date + datetime.timedelta(days=31)
    end_date.replace(day=1)

    # select clicks for this ad grouped by day depends on database engine
    if settings.DATABASE_ENGINE == 'sqlite3':
        select_data = {"d": """strftime('%%m/%%d/%%Y', datetime)"""}
    else:
        select_data = {"d": """TO_CHAR(datetime, 'MM/DD/YY')"""}
    clicks = Click.objects.filter(ad__pk=pk,
                                  datetime__gte=start_date,
                                  datetime__lte=end_date).extra(select=select_data).values('d').annotate(Count("pk")).order_by()

    c = calendar.Calendar(calendar.SUNDAY)

    # Get clicks on day
    by_day = dict([
            (dom, list(items)[0])
            for dom, items in itertools.groupby(clicks, lambda c: c['d'].split('/')[1].lstrip('0'))
            ])

    # Get all the days in the month
    days = dict([[day, by_day.get(str(day), 0)] for day in c.itermonthdays(start_date.year, start_date.month)
                 if day != 0
                 and day <= datetime.datetime.now().day
                 and start_date.month == datetime.datetime.now().month
                 ])

    # match all the days with the click value
    clicks = [[mktimetuple(day[0], start_date), click_count(day[1])] for day in days.items()]

    click_data = {}
    click_data['clicks'] = clicks
    click_data['start'] = start_date
    click_data['end'] = end_date

    return click_data
