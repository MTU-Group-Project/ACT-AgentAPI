from firebase_functions import https_fn
from firebase_admin import initialize_app

import json, api
from status import StatusException

initialize_app()

@https_fn.on_request()
def get_report(req: https_fn.Request) -> https_fn.Response:

	
	try:
		output = api.main(req)
	
	# Handle exceptions, get status from Exception or default to 500
	except Exception as e:
		print("[ERROR]", e)
		if issubclass(type(e), StatusException):
			status = e.status
		else:
			status = 500
		output = {"error": str(e)}, status

	# If output from API is not a content/status tuple, treat as 200
	if type(output) != tuple:
		output = output, 200
		
	# Output JSON
	return https_fn.Response(
		json.dumps(output[0]),
		status=output[1],
		headers=[
			("Content-Type", "application/json")
		]
	)