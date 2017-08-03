from django.conf.urls import url
from django.contrib import admin

from activitypub.views import person, note, notes, inbox, outbox
from activitypub.views import followers, following, activity

urlpatterns = [
    url(r'^@(\w+)/notes/(\w+)', note, name="note"),
    url(r'^@(\w+)/notes', notes, name="notes"),
    url(r'^@(\w+)/following', following, name="following"),
    url(r'^@(\w+)/followers', followers, name="followers"),
    url(r'^@(\w+)/inbox', inbox, name="inbox"),
    url(r'^@(\w+)/outbox/(\w+)', activity, name="activity"),
    url(r'^@(\w+)/outbox', outbox, name="outbox"),
    url(r'^@([^/]+)$', person, name="person"),
    url(r'^@([^/]+)/notes', notes),
    url(r'^admin/', admin.site.urls),
]
