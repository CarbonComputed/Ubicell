from mongoengine import *

class Notification(EmbeddedDocument):
	Message = StringField(required=True)
	Read = BooleanField(default=False)

class FriendRequestNot(Notification):
	Friend = ObjectIdField()

class TagNot(Notification):
	Friend = ObjectIdField()
	PostId = ObjectIdField()
	ReplyId = ObjectIdField()