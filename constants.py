#!/usr/bin/env python


USER_REGEX='([a-z\d.]{5,})/?'

class RespSuccess:
	DEFAULT_SUCCESS = 200

class RespError:
	DEFAULT_ERROR = 500
	DUPLICATE_ERROR = 501
	NOT_REGISTERED_ERROR = 502
	UNAUTHORIZED_ACTION = 503

class UserStatus:
	USER_REQ = 1
	USER_ACC = 2
	USER_NEI = 3
	USER_ME = 4
	USER_FRI = 5

class Action:
	FRIEND_RESP = 1