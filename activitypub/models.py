import json

from django.db.models import Model, ForeignKey, CharField, TextField, BooleanField
from django.db.models import BinaryField, DateField, ManyToManyField, SET_NULL
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings
from django.urls import reverse

def uri(name, *args):
    domain = settings.ACTIVITYPUB_DOMAIN
    path   = reverse(name, args=args)
    return "http://{domain}{path}".format(domain=domain, path=path)

class URIs(object):

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

class Person(Model):
    ap_id     = TextField(null=True)
    remote    = BooleanField(default=False)
    username  = CharField(max_length=100)
    name      = CharField(max_length=100)
    following = ManyToManyField('self', symmetrical=False, related_name='followers')

    @property
    def uris(self):
        if self.remote:
            return URIs(id=self.ap_id)

        return URIs(
            id=uri("person", self.username),
            following=uri("following", self.username),
            followers=uri("followers", self.username),
            outbox=uri("outbox", self.username),
            inbox=uri("inbox", self.username),
        )

    def to_activitystream(self):
        json = {
            "type": "Person",
            "id": self.uris.id,
            "name": self.name,
            "preferredUsername": self.username,
        }

        if not self.remote:
            json.update({
                "following": self.uris.following,
                "followers": self.uris.followers,
                "outbox": self.uris.outbox,
                "inbox": self.uris.inbox,
            })
        return json

class Note(Model):
    ap_id   = TextField(null=True)
    remote  = BooleanField(default=False)
    person  = ForeignKey(Person, related_name='notes',null=True,on_delete=SET_NULL)
    content = CharField(max_length=500)
    likes   = ManyToManyField(Person, related_name='liked')

    @property
    def uris(self):
        if self.remote:
            ap_id = self.ap_id
        else:
            ap_id = uri("note", self.person.username, self.id)
        return URIs(id=ap_id)

    def to_activitystream(self):
        return {
            "type": "Note",
            "id": self.uris.id,
            "content": self.content,
            "actor": self.person.uris.id,
        }

class Activity(Model):

    ap_id      = TextField()
    payload    = BinaryField()
    created_at = DateField(auto_now_add=True)
    person     = ForeignKey(Person, related_name='activities',null=True,on_delete=SET_NULL)
    remote     = BooleanField(default=False)

    @property
    def uris(self):
        if self.remote:
            ap_id = self.ap_id
        else:
            ap_id = uri("activity", self.person.username, self.id)
        return URIs(id=ap_id)

    def to_activitystream(self):
        payload = self.payload.decode("utf-8")
        data = json.loads(payload)
        data.update({
            "id": self.uris.id
        })
        return data

@receiver(post_save, sender=Person)
@receiver(post_save, sender=Note)
@receiver(post_save, sender=Activity)
def save_ap_id(sender, instance, created, **kwargs):
    if created and not instance.remote:
        instance.ap_id = instance.uris.id
        instance.save()
