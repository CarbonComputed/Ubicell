from mongoengine import *

class Club(Document):
    Name = StringField()
    About = StringField()
    University = ObjectIdField()
    Members = ListField(ObjectIdField())
    MemberRequests = ListField(ObjectIdField())
    Admins = ListField(ObjectIdField())
    BanList = ListField(ObjectIdField())
    Private = BooleanField()

