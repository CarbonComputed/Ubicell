def find(lst,object_att,object_val):

	for obj in lst:
		if obj.__dict__['_data'].get(object_att,None) == object_val:
			return obj
	return None