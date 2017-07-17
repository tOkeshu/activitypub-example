ActivityPub example server
==========================

This is an example server implementing a few basic features of [activitypub](https://www.w3.org/TR/activitypub/).

Features
--------

Outbox:

- [ ] Accept Create activities
- [ ] Accept Follow activities
- [ ] Accept Like activities
- [ ] Accept non-activity objects and convert them to a Create
  activity (only accepts Note objects for now since it is an example
  server)

Delivery:

- [ ] Handle `to` audience
- [ ] Handle `cc` audience
- [ ] Handle `bto` and `bcc`

Inbox:

- [ ] Accept Create activities
- [ ] Accept Follow activities
- [ ] Accept Like activities

License
-------

This ActivityPub example server is released under the terms of the
[GNU Affero General Public License v3](http://www.gnu.org/licenses/agpl-3.0.html)
or later.
