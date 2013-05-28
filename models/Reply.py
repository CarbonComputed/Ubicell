import gridfs
import json
#from constants import *

from bson.objectid import ObjectId

from mongoengine import *

import datetime

class Reply(EmbeddedDocument):
    id = ObjectIdField()
    FriendId = ObjectIdField()
    UserId = ObjectIdField()
    ParentId = ObjectIdField()
    Hotness = FloatField()
    Message = StringField()
    Time = DateTimeField(default=datetime.datetime.now)
    Upvotes = IntField()
    Downvotes = IntField()