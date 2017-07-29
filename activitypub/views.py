from urllib.parse import urlparse
import json
import requests

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from activitypub.models import Person, Note
from activitypub import activities
from activitypub.activities import as_activitystream

def noop(*args, **kwargs):
    pass

def person(request, username):
    person = get_object_or_404(Person, username=username)
    return JsonResponse(activities.Person(person).to_json(context=True))

def note(request, username, note_id):
    note = get_object_or_404(Note, pk=note_id)
    return JsonResponse(activities.Note(note).to_json(context=True))

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

    if activity.type == "Follow":
        # if activity.object.type != "Person":
        #     raise Exception("Sorry, you can only follow Persons objects")

        followed = get_or_create_remote_person(activity.object)
        person.following.add(followed)

        activity.actor = person.uris.id
        activity.to = followed.uris.id
        deliver(activity)
        return HttpResponse() # TODO: code 202

    raise Exception("Invalid Request")

def deliver(activity):
    audience = activity.get_audience()
    activity = activity.strip_audience()
    audience = get_final_audience(audience)
    print("audience", audience)
    for ap_id in audience:
        deliver_to(ap_id, activity)

def get_final_audience(audience):
    final_audience = []
    for ap_id in audience:
        obj = dereference(ap_id)
        if isinstance(obj, activities.Collection):
            final_audience += [item.id for item in obj.items]
        elif isinstance(obj, activities.Actor):
            final_audience.append(obj.id)
    return set(final_audience)

def deliver_to(ap_id, activity):
    obj = dereference(ap_id)
    if not getattr(obj, "inbox", None):
        # XXX: log this
        return

    res = requests.post(obj.inbox, json=activity.to_json(context=True))
    if res.status_code != 200:
        msg = "Failed to deliver activity {0} to {1}"
        msg = msg.format(activity.type, obj.inbox)
        raise Exception(msg)

def dereference(ap_id, type=None):
    res = requests.get(ap_id)
    if res.status_code != 200:
        raise Exception("Failed to dereference {0}".format(ap_id))

    return json.loads(res.text, object_hook=as_activitystream)

def get_or_create_remote_person(ap_id):
    try:
        person = Person.objects.get(ap_id=ap_id)
    except Person.DoesNotExist:
        person   = dereference(ap_id)
        hostname = urlparse(person.id).hostname
        username = "{0}@{1}".format(person.preferredUsername, hostname)
        person = Person(
            username=username,
            name=person.name,
            ap_id=person.id,
            remote=True,
        )
        person.save()
    return person

@csrf_exempt
def inbox(request, username):
    person = get_object_or_404(Person, username=username)
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    payload  = request.body.decode("utf-8")
    activity = json.loads(payload, object_hook=as_activitystream)
    activity.validate()
    print(activity)

    if activity.type == "Create":
        handle_note(activity)
    elif activity.type == "Follow":
        handle_follow(activity)
    return HttpResponse()

def handle_note(activity):
    if isinstance(activity.actor, activities.Actor):
        ap_id = activity.actor.id
    elif isinstance(activity.actor, str):
        ap_id = activity.actor

    person = get_or_create_remote_person(ap_id)

    try:
        note = Note.objects.get(ap_id=activity.object.id)
    except Note.DoesNotExist:
        note = None
    if note:
        return

    note = Note(
        content=activity.object.content,
        person=person,
        ap_id=activity.object.id,
        remote=True
    )
    note.save()
    print(activities.Note(note))

def handle_follow(activity):
    followed = get_object_or_404(Person, ap_id=activity.object)

    if isinstance(activity.actor, activities.Actor):
        ap_id = activity.actor.id
    elif isinstance(activity.actor, str):
        ap_id = activity.actor

    follower = get_or_create_remote_person(ap_id)
    followed.followers.add(follower)

def notes(request, username):
    person = get_object_or_404(Person, username=username)
    collection = activities.OrderedCollection(person.notes.all())
    # collection = activities.OrderedCollection(
    #     person.notes.all(),
    #     id=person.uris.notes
    # )
    return JsonResponse(collection.to_json(context=True))

def followers(request, username):
    person = get_object_or_404(Person, username=username)
    followers = activities.OrderedCollection(person.followers.all())
    return JsonResponse(followers.to_json(context=True))

def following(request, username):
    person = get_object_or_404(Person, username=username)
    following = activities.OrderedCollection(person.following.all())
    return JsonResponse(following.to_json(context=True))
