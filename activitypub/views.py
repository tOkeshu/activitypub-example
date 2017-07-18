from urllib.parse import urlparse
import json
import requests

from django.http import JsonResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from activitypub.models import Person, Note
from activitypub import activities
from activitypub.activities import as_activitystream

def person(request, username):
    person = get_object_or_404(Person, username=username)
    return JsonResponse(activities.Person(person).to_json(context=True))

