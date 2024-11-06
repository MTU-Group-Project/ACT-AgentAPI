from firebase_functions import https_fn
from firebase_admin import initialize_app, db

import json

initialize_app()

@https_fn.on_request()
def get_report(req: https_fn.Request) -> https_fn.Response:
	output = {}
	try:
		# Get stock from URL parameter
		if "stock" not in req.args:
			raise Exception("No stock provided")
		stock = req.args["stock"]

		#Input validation
		if len(stock) > 4 or len(stock) < 2:
			raise Exception("Invalid stock length")
		if not stock.isalpha():
			raise Exception("Stock must only contain letters")
		if not stock.isupper():
			raise Exception("Stock must only contain uppercase letters")

		# Check if a report already exists in database
		cache_ref = db.reference(f"agents/cache/stock/{stock}/report")
		report = cache_ref.get()

		# If report does not exist, call the crew to generate one
		if not report:
			# For performance reasons, agents are only imported if they are needed
			from agents.src.act_agents.crew import ActAgentsCrew
			
			# Run the crew to generate a report
			report = ActAgentsCrew().crew().kickoff(inputs = {
				"stock": stock
			})

			# Save to database
			cache_ref.set(report)

		output = {
			"stock": stock,
			"report": report
		}
	
	# Handle exceptions
	except Exception as e:
		output = {"error": str(e)}
		
	# Output JSON
	return https_fn.Response(
		json.dumps(output),
		headers=[
			("Content-Type", "application/json")
		]
	)