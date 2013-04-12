from threading import Thread
from functools import wraps

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

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def run_async(func):
  @wraps(func)
  def async_func(*args, **kwargs):
    func_hl = Thread(target = func, args = args, kwargs = kwargs)
    func_hl.start()
    return func_hl

  return async_func