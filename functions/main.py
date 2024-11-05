from firebase_functions import https_fn
from firebase_admin import initialize_app

import json
from ... import src/crew

initialize_app()

@https_fn.on_request()
def get_report(req: https_fn.Request) -> https_fn.Response:
	in_data = {
		"stock": "AAPL"
	}
	
	out_data = {
		"stock": in_data["stock"]
	}
	
	return https_fn.Response(
		json.dumps(out_data),
		headers=[
			("Content-Type", "application/json")
		]
	)