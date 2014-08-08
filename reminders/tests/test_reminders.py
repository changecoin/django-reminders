from datetime import timedelta
from django.contrib.auth.models import User, AnonymousUser
from django.template import Template, Context
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone
from reminders.models import Dismissal

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
                              "{% reminders as reminder %}" \
                              "{% if reminder %}" \
                              "Message: {{ reminder.message }} " \
                              "URL: {{ reminder.dismiss_url }}" \
                              "{% else %}No reminders" \
                              "{% endif %}"
        self.usual_settings = {
            "show_to_bob": {
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

            # Authenticated Bob will get just the blanket message because it's alphabetically first
            bob.is_authenticated.return_value = True
            setattr(request, 'user', bob)

            t = Template(self.usual_template).render(Context({'request': request}))
            self.assertEqual(t.strip(),
                             "Message: Remember to take out the trash URL: /reminders/dismiss/blanket/")

            # Bob dismisses that one
            Dismissal.objects.create(label="blanket", user=bob)

            # Now Bob gets no messages, even though his name is Bob, because he just recently dismissed a message
            t = Template(self.usual_template).render(Context({'request': request}))
            self.assertEqual(t.strip(), "No reminders")

            # Authenticated Wonko will just get the blanket message
            wonko = User.objects.get(username='wonko')
            wonko.is_authenticated = mock.MagicMock()
            wonko.is_authenticated.return_value = True
            setattr(request, 'user', wonko)

            t = Template(self.usual_template).render(Context({'request': request}))
            self.assertEqual(t.strip(), "Message: Remember to take out the trash URL: /reminders/dismiss/blanket/")

            # Both wonko dismisses the trash/blanket one too
            Dismissal.objects.create(label="blanket", user=wonko)

            # Authenticated Wonko will get no messages
            t = Template(self.usual_template).render(Context({'request': request}))
            self.assertEqual(t.strip(), "No reminders")

            # Authenticated Bob will get no messages
            setattr(request, 'user', bob)
            t = Template(self.usual_template).render(Context({'request': request}))
            self.assertEqual(t.strip(), "No reminders")

            # Now it's been a couple days since Bob dismissed that blanket one
            bobs_dismissal = Dismissal.objects.get(label="blanket", user=bob)
            bobs_dismissal.dismissed_at = timezone.now() - timedelta(days=2)
            bobs_dismissal.save()

            # Now Bob will get the show-to-bob message
            t = Template(self.usual_template).render(Context({'request': request}))
            self.assertEqual(t.strip(), "Message: Remember to put on pants URL: /reminders/dismiss/show_to_bob/")