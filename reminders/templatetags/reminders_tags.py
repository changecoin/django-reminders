from datetime import timedelta
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.importlib import import_module
from django.utils.safestring import mark_safe

from reminders.models import Dismissal


register = template.Library()


def load_callable(path_to_callable):
    try:
        mod_name, func_name = path_to_callable.rsplit(".", 1)
    except ValueError:
        raise Exception("Improperly configured.")
    try:
        mod = import_module(mod_name)
    except ImportError:
        raise Exception("Could not import %s" % mod_name)
    try:
        func = getattr(mod, func_name)
    except AttributeError:
        raise Exception("The module '%s' does not contain '%s'." % (mod_name, func_name))
    return func


def is_dismissed(label, dismissal_type, request):
    if dismissal_type == "session":
        dismissed = label in request.session
    elif dismissal_type == "permanent":
        dismissed = Dismissal.objects.filter(user=request.user, label=label).exists()
    else:
        dismissed = False
    return dismissed


def recently_dismissed_something(user):
    time_ago = timezone.now() - timedelta(days=1)
    return Dismissal.objects.filter(user=user, dismissed_at__gt=time_ago).exists()


class RemindersNode(template.Node):

    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        if len(bits) != 3:
            raise template.TemplateSyntaxError
        return cls(as_var=bits[2])

    def __init__(self, as_var):
        self.as_var = as_var

    def render(self, context):
        request = context["request"]
        show_reminder = None

        # Don't bother if they aren't logged in or if they just recently dismissed another message
        if request.user.is_authenticated() and not recently_dismissed_something(request.user):

            # Make sure the order is deterministic here so they get the same
            # reminder on each screen until they dismiss it
            for label in sorted(settings.REMINDERS.keys()):
                reminder = settings.REMINDERS[label]

                if not is_dismissed(label, reminder.get("dismissable"), request):
                    message = reminder["message"]
                    if not callable(message):
                        message = load_callable(message)

                    url = None
                    if reminder.get("dismissable") != "no":
                        url = reverse("reminders_dismiss", kwargs={"label": label})

                    result = message(request.user)
                    if result and isinstance(result, basestring):
                        show_reminder = {"message": mark_safe(result),
                                         "dismiss_url": url}
                        # just one reminder at a time, spaced according to time_ago in recently_dismissed_something
                        break

        context[self.as_var] = show_reminder
        return ""


@register.tag
def reminders(parser, token):
    """
    Usage::
        {% reminders as var %}

    Returns a list of reminders
    """
    return RemindersNode.handle_token(parser, token)
