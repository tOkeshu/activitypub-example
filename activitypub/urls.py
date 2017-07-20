from django.conf.urls import url
from django.contrib import admin

from activitypub.views import person, note, new_note, notes, inbox, outbox
from activitypub.views import followers, noop

urlpatterns = [
    url(r'^@(\w+)/notes/(\w+)', note, name="note"),
    url(r'^@(\w+)/outbox', outbox, name="outbox"),
    url(r'^@([^/]+)$', person, name="person"),
    url(r'^admin/', admin.site.urls),
]
