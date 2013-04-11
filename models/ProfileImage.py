from mongoengine import *

class ProfileImage(Document):
	Owner = ObjectIdField()
	Image = FileField(collection_name="profile_images")