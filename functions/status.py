# 400 - Bad Request
class BadRequest(Exception):
	status = 400

# 401 - Unauthorized
class Unauthorized(Exception):
	status = 401

# 403 - Forbidden
class Forbidden(Exception):
	status = 403

# 404 - Not Found
class NotFound(Exception):
	status = 404

# 500 - Internal Server Error
class InternalServerError(Exception):
	status = 500