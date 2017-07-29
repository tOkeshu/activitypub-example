from django.conf.urls import url
from django.contrib import admin

from activitypub.views import person, note, notes, inbox, outbox, followers

urlpatterns = [
    url(r'^@(\w+)/notes/(\w+)', note, name="note"),
    url(r'^@(\w+)/notes', notes, name="notes"),
    url(r'^@(\w+)/followers', followers, name="followers"),
    url(r'^@(\w+)/inbox', inbox, name="inbox"),
    url(r'^@(\w+)/outbox', outbox, name="outbox"),
    url(r'^@([^/]+)$', person, name="person"),
    url(r'^admin/', admin.site.urls),
]
