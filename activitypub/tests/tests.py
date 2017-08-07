from unittest.mock import patch
import json

from django.test import TestCase, Client
from django.conf import settings

from activitypub.models import Person

settings.ACTIVITYPUB_DOMAIN = "example.com"

class PersonTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create(username="foo", name="Foo")

    def test_uris(self):
        uris = (
            self.person.uris.following,
            self.person.uris.followers,
            self.person.uris.outbox,
            self.person.uris.inbox,
        )

        expected = (
            "http://example.com/@foo/following",
            "http://example.com/@foo/followers",
            "http://example.com/@foo/outbox",
            "http://example.com/@foo/inbox",
        )
        self.assertEqual(uris, expected)

    def test_ap_id(self):
        self.assertEqual(self.person.uris.id, self.person.ap_id)

        bar = Person(
            username="bar",
            name="Bar",
            ap_id="http://bar.com/@bar",
            remote=True
        )
        self.assertEqual(bar.ap_id, "http://bar.com/@bar")
        self.assertEqual(bar.uris.id, bar.ap_id)

class NoteTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create(username="foo", name="Foo")
        self.note = self.person.notes.create(content="Hello world")

    def test_ap_id(self):
        self.assertEqual(self.note.uris.id, "http://example.com/@foo/notes/{0}".format(self.note.id))
        self.assertEqual(self.note.uris.id, self.note.ap_id)

class Outbox(TestCase):
    def post(self, path, data):
        payload = json.dumps(data)
        return self.client.post(path, payload, content_type='application/json')

    def setUp(self):
        self.patched = patch('activitypub.views.deliver')
        self.patched.start()

        self.client = Client()
        self.person = Person.objects.create(username="foo", name="Foo")

    def tearDown(self):
        self.patched.stop()

    def test_post_note(self):
        response = self.post('/@foo/outbox', {"type": "Note", "content": "Hi!"})
        note = self.person.notes.all()[0]

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get("Location"), note.ap_id)

        self.assertEqual(note.content, "Hi!")
