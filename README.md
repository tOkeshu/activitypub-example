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
