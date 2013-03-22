from mongoengine import *

class School(EmbeddedDocument):
	University = ObjectIdField(required=True)
	Major = StringField(required=True)
	GradYear = IntField(min_value=2000,max_value=2050,required=True)

if __name__ == "__main__":
	pass