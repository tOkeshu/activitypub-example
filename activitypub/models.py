from django.db.models import Model, ForeignKey, CharField, TextField, BooleanField
from django.db.models import ManyToManyField
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

@receiver(post_save, sender=Person)
@receiver(post_save, sender=Note)
def save_ap_id(sender, instance, created, **kwargs):
    if created and not instance.remote:
        instance.ap_id = instance.uris.id
        instance.save()
    
