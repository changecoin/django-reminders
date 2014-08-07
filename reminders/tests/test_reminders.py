from django.contrib.auth.models import User, AnonymousUser
from django.template import Template, Context
from django.test import TestCase
from django.test.client import RequestFactory

import mock


def show_to_bob(user):
    if user.first_name == 'Bob':
        return "Remember to put on pants"


def show_everyone(user):
    return "Remember to take out the trash"


class RemindersTestCase(TestCase):

    def setUp(self):
        self.bob = User.objects.create_user('bob')
        self.bob.first_name = 'Bob'
        self.bob.save()
        self.wonko = User.objects.create_user('wonko')
        self.wonko.first_name = 'Wonko'
        self.wonko.save()

        self.usual_template = "{% load reminders_tags %}" \
                              "{% reminders as user_reminders %}" \
                              "{% for reminder in user_reminders %}" \
                              "Message: {{ reminder.message }} " \
                              "URL: {{ reminder.dismiss_url }}" \
                              "{% empty %}No reminders" \
                              "{% endfor %}"
        self.usual_settings = {
            "email_address": {
                "message": "reminders.tests.test_reminders.show_to_bob",
                "dismissable": "permanent"
            },
            "blanket": {
                "message": "reminders.tests.test_reminders.show_everyone",
                "dismissable": "permanent"
            }
        }

    def test_template_tag(self):
        with self.settings(REMINDERS=self.usual_settings):
            self.factory = RequestFactory()
            request = self.factory.get('/')

            # Anonymous user will get no reminders
            setattr(request, 'user', AnonymousUser())

            t = Template(self.usual_template).render(Context({'request': request}))
            self.assertEqual(t.strip(), "No reminders")

            # Unauthenticated bob will get no reminders
            bob = User.objects.get(username='bob')
            bob.is_authenticated = mock.MagicMock()
            bob.is_authenticated.return_value = False
            setattr(request, 'user', bob)

            t = Template(self.usual_template).render(Context({'request': request}))
            self.assertEqual(t.strip(), "No reminders")

            # Authenticated Bob will get both the blanket message and the bob-specific message
            bob.is_authenticated.return_value = True
            setattr(request, 'user', bob)

            t = Template(self.usual_template).render(Context({'request': request}))
            self.assertEqual(t.strip(),
                             "Message: Remember to take out the trash URL: /reminders/dismiss/blanket/" +
                             "Message: Remember to put on pants URL: /reminders/dismiss/email_address/")

            # First name is no longer Bob, so now he'll get just the blanket message
            bob.first_name = "Baobab"
            bob.save()

            t = Template(self.usual_template).render(Context({'request': request}))
            self.assertEqual(t.strip(), "Message: Remember to take out the trash URL: /reminders/dismiss/blanket/")

            # Authenticated Wonko will just get the blanket message
            wonko = User.objects.get(username='wonko')
            wonko.is_authenticated = mock.MagicMock()
            wonko.is_authenticated.return_value = True
            setattr(request, 'user', wonko)

            t = Template(self.usual_template).render(Context({'request': request}))
            self.assertEqual(t.strip(), "Message: Remember to take out the trash URL: /reminders/dismiss/blanket/")
