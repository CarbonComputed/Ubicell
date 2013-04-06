def find(lst,object_att,object_val):

	for obj in lst:
		if obj.__dict__['_data'].get(object_att,None) == object_val:
			return obj
	return None


def index(lst,object_att,object_val):
	ctr = 0
	for obj in lst:
		if obj.__dict__['_data'].get(object_att,None) == object_val:
			return ctr
		ctr += 1
	return -1