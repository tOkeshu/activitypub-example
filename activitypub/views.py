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

@csrf_exempt
def outbox(request, username):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    payload = request.body.decode("utf-8")
    activity = json.loads(payload, object_hook=as_activitystream)
    person   = get_object_or_404(Person, username=username)

    if activity.type == "Note":
        obj = activity
        activity = activities.Create(
            to=person.uris.followers,
            actor=person.uris.id,
            object=obj
        )
        
    activity.validate()
    
    if activity.type == "Create":
        if activity.object.type != "Note":
            raise Exception("Sorry, you can only create Notes objects")

        content = activity.object.content
        note    = Note(content=content, person=person)
        note.save()

        # TODO: check for actor being the right actor object
        activity.object.id = note.uris.id
        deliver(activity)
        return HttpResponseRedirect(note.uris.id)

    raise Exception("Invalid Request")

def deliver(activity):
    pass

