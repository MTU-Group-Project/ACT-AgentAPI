class StatusException(Exception):
	status = 0

# 400 - Bad Request
class BadRequest(StatusException):
	status = 400

# 401 - Unauthorized
class Unauthorized(StatusException):
	status = 401

# 403 - Forbidden
class Forbidden(StatusException):
	status = 403

# 404 - Not Found
class NotFound(StatusException):
	status = 404

# 500 - Internal Server Error
class InternalServerError(StatusException):
	status = 500