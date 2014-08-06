from django.conf.urls import patterns, url


urlpatterns = patterns(
    "",
    url(r"^dismiss/(?P<label>.+)/$", "reminders.views.dismiss", name="reminders_dismiss"),
)
