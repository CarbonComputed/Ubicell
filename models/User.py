import gridfs
import json
#from constants import *

from bson.objectid import ObjectId

from mongoengine import *
import datetime

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.+-]+\.edu$'
USERNAME_REGEX = r'[a-z\d.]{5,}'

GENDERS = ['Male', 'Female']



class SubClub(EmbeddedDocument):
	Name = StringField()
	Id = ObjectIdField()

class User(Document):

	FirstName = StringField(max_length=20,required=True)
	LastName = StringField(max_length=20,required=True)
	UserName = StringField(regex=USERNAME_REGEX,max_length=20,required=True,unique=True)
	Password = StringField(required=True)
	About = StringField(max_length=400,required=False)
	Email = EmailField(regex = EMAIL_REGEX,required = True,unique=True)
	Gender = StringField(required=True,choices=GENDERS)
	School = EmbeddedDocumentField('School')
	ProfileImg = ObjectIdField()
	date_created = DateTimeField(default=datetime.datetime.now)
	Friends = ListField(ObjectIdField())
	FriendsRequesting = ListField(ObjectIdField())
	FriendsRequested = ListField(ObjectIdField())
	Wall = ListField(EmbeddedDocumentField('Post'))
	Nots = ListField(EmbeddedDocumentField('Notification'))
	Clubs = ListField(EmbeddedDocumentField('SubClub'))
	Active = BooleanField(default=False)
	RegId = ObjectIdField()

if __name__ == "__main__":
	connect('uplace')
	user = User.objects(FirstName='k2')
	user = User(Gender="Male",FirstName = 'k3',LastName ='C3',UserName='test4',Password='test4',Email='asdfasad2f@rit.edu')
	user.save()
	# print user.first().id
	# print User.objects().count()



