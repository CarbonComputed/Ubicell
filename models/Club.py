from mongoengine import *

class Club(Document):
    Name = StringField()
    About = StringField()
    University = ObjectIdField()
    Wall = ListField(EmbeddedDocumentField('Post'))
    Members = ListField(ObjectIdField())
    Admins = ListField(ObjectIdField())
    BanList = ListField(ObjectIdField())

