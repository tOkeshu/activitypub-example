ActivityPub example server
==========================

This is an example server implementing a few basic features of [activitypub](https://www.w3.org/TR/activitypub/).

Because ActivityPub is quite generic, the goal here is not the implement every aspect of ActivityPub but just a coherent subset that can be used for understanding the protocol as well as for testing. Thus the use case is microblogging: users can only publish or like notes and follow each others.

Features
--------

Outbox:

- [X] Accept Create activities
- [ ] Accept Follow activities
- [ ] Accept Like activities
- [X] Accept non-activity objects and convert them to a Create
  activity (only accepts Note objects for now since it is an example
  server)

Delivery:

- [X] Handle `to` audience
- [X] Handle `cc` audience
- [X] Handle `bto` and `bcc`
- [X] Handle `audience` audience

Inbox:

- [X] Accept Create activities
- [ ] Accept Follow activities
- [ ] Accept Like activities

Getting started
---------------

Install requirements (probably in a virtualenv):

  $ pip install django requests

Clone this repository:

  $ git clone https://github.com/tOkeshu/activitypub-example.git

Run the migrations

  $ cd activitypub
  $ ./manage.py migrate

Run the server

  $ ./manage.py runserver

Testing the federation
----------------------

Testing the federation is a tat trickier.
You can use a reverse proxy to simulate remote servers.

First add two new hosts in your hosts file:

  $ cat /etc/hosts
  ...
  127.0.1.1	alice.local bob.local
  ...

Then add two new virtual hosts for alice.local and bob.local.
Here is an example nginx configuration file to achieve that:

    server {
        listen 80;
        index index.html index.htm;

        server_name alice.local;
        server_name_in_redirect off;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header X-Forwarded-Host $host;
        }
    }

Copy the file and change `alice.local` to `bob.local` and the port to `8001`.
You'll also need two different Django configuration files. So copy `activitypub/settings.py` to `activitypub/settings-bob.py` and change the following values:

    $ cat activitypub/settings-bob.py
    ...
    ACTIVITYPUB_DOMAIN = "alice.local" # or bob.local
    ...
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'alice.sqlite3'), # or bob.sqlite3
        }
    }


Now you can run the migrations for alice (default) and bob:

    $ ./manage.py migrate --settings=activitypub.settings
    $ ./manage.py migrate --settings=activitypub.settings-bob

Finally run the two servers in different terminals:

    $ ./manage.py runserver # alice
    $ ./manage.py runserver 8001 --setttings=activitypub.settings-bob

Check that the servers are reachable via the correct hosts:

  - [http://alice.local](http://alice.local)
  - [http://bob.local](http://bob.local)

If all works correctly they should be able to reach each others. To verify that, we need to first create users. The simplest way is to do it via the python shell:

    $ ./manage.py shell
    ...
    >>> from activitypub.models import Person
    >>> alice = Person(username="alice", name="Alice in Wonderland")
    >>> alice.save()

Alice's actor representation should be available at http://alice.local/@alice.
Now do that same for Bob:

    $ ./manage.py shell --settings=activitypub.settings-bob
    ...
    >>> from activitypub.models import Person
    >>> bob = Person(username="bob", name="Robert Paulson")
    >>> bob.save()

Again, Bob's representation should be available at http://bob.local/@bob.
Let's make Alice follow bob:

    $ curl -X POST 'http://alice.local/@alice/outbox' -H "Content-Type: application/activity+json" -d '{"type": "Follow", "object": "http://bob.local/@bob"}'

If everything went fine, we should be able to find Bob in Alice's following collection and Alice in Bob's followers collection:

- [http://alice.local/@alice/following](http://alice.local/@alice/following)
- [http://bob.local/@bob/followers](http://bob.local/@bob/followers)

If Bob publishes a note as follow:

    $ curl -X POST 'http://bob.local/@bob/outbox' -H "Content-Type: application/activity+json" -d '{"type": "Note", "content": "Good morning!"}'

We should be able to find the new note on Alice's instance: http://alice.local/@bob@bob.local/notes

API
---

Create a new note:

    POST /@alice/outbox HTTP/1.1
    Host: social.example.com
    Content-Type: application/activity+json

    {
      "type": "Create",
      "to": "https://social.example.com/@alice/followers",
      "object": {
        "type": "Note",
        "content": "Hello world!"
      }
    }

Create a new note without an activity:

    POST /@alice/outbox HTTP/1.1
    Host: social.example.com
    Content-Type: application/activity+json

    {
      "type": "Note",
      "content": "Hello world!"
    }

Follow someone:

    POST /@alice/outbox HTTP/1.1
    Host: social.example.com
    Content-Type: application/activity+json

    {
      "type": "Follow",
      "object": "https://social.example.com/@bob"
    }

License
-------

This ActivityPub example server is released under the terms of the
[GNU Affero General Public License v3](http://www.gnu.org/licenses/agpl-3.0.html)
or later.
