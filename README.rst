================
django-reminders
================

.. image:: https://img.shields.io/travis/eldarion/django-reminders.svg
    :target: https://travis-ci.org/eldarion/django-reminders

.. image:: https://img.shields.io/coveralls/eldarion/django-reminders.svg
    :target: https://coveralls.io/r/eldarion/django-reminders

.. image:: https://img.shields.io/pypi/dm/django-reminders.svg
    :target:  https://pypi.python.org/pypi/django-reminders/

.. image:: https://img.shields.io/pypi/v/django-reminders.svg
    :target:  https://pypi.python.org/pypi/django-reminders/

.. image:: https://img.shields.io/badge/license-BSD-blue.svg
    :target:  https://pypi.python.org/pypi/django-reminders/


a user reminder app for site builders to guide users through completion of activities


Our Mods
--------
This fork includes the following modifications over the original:

#. It is compatible with Django 1.6
#. It shows reminders only to logged-in users
#. It has some tests
#. It spaces reminders out so that if a user has recently dismissed a message, it waits a day before displaying another one to that user.
#. It introduces a 'priority' parameter to the reminder configuration in settings, determining which reminders are displayed first.
#. It fixes a bug in which a permanently-dismissible reminder left over from an active session, now finding itself in an inactive session, was throwing errors when retrieving the newly-non-existent request user.

Documentation
-------------

Documentation can be found online at http://django-reminders.readthedocs.org/.


