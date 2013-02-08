#!/usr/bin/env python


USER_REGEX='([a-z\d.]{5,})/?'

class RespSuccess:
	DEFAULT_SUCCESS = 200

class RespError:
	DEFAULT_ERROR = 500
	DUPLICATE_ERROR = 501
	NOT_REGISTERED_ERROR = 502
	UNAUTHORIZED_ACTION = 503

class FriendStatus:
	FRIEND_REQ = 1
	FRIEND_ACC = 2
	FRIEND_NEI = 3

