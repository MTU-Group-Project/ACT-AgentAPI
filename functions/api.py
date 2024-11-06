from firebase_admin import db

import threading, status
from tasks import task

def main(req):
	taskThread = threading.Thread(target=task)
	taskThread.start()
	
	# Get stock from URL parameter
	if "stock" not in req.args:
		raise status.BadRequest("No stock provided")
	stock = req.args["stock"]

	#Input validation
	if len(stock) > 4 or len(stock) < 2:
		raise status.BadRequest("Invalid stock length")
	if not stock.isalpha():
		raise status.BadRequest("Stock must only contain letters")
	if not stock.isupper():
		raise status.BadRequest("Stock must only contain uppercase letters")

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

	return {
		"stock": stock,
		"report": report
	}