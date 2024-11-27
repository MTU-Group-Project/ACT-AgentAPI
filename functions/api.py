from firebase_admin import db

import threading, status

def main(req):
	# Get stock from URL parameter
	if "stock" not in req.args:
		raise status.BadRequest("No stock provided")
	stock = req.args["stock"]

	vaidation_stock = stock.replace("-", "")

	#Input validation
	if len(vaidation_stock) > 6	 or len(vaidation_stock) < 2:
		raise status.BadRequest("Invalid stock length")
	if not vaidation_stock.isalpha():
		raise status.BadRequest("Stock must only contain letters")
	if not vaidation_stock.isupper():
		raise status.BadRequest("Stock must only contain uppercase letters")

	# Get details about this stock from database
	ref = db.reference(f"agents/stock/{stock}")
	stock_data = ref.get() or {
		"state": "empty"
	}

	# Default state
	if "state" not in stock_data:
		stock_data["state"] = "empty"

	# If an error occured previously, clear it from the database
	if "error" in stock_data:
		ref.update({"error": None})
		return stock_data

	# If report does not exist, call the crew to generate one
	if "report" not in stock_data and stock_data["state"] != "generating":
		# Create thread for running crew and start it
		reportThread = threading.Thread(target=run_crew, args=[ref, stock])
		print("[THREAD] Starting...")
		reportThread.start()
		# Set state to generating and store in database
		stock_data["state"] = "generating"
		# Clear any previous data
		stock_data["last_agent"] = None
		stock_data["error"] = None
		
		ref.update(stock_data)
		del stock_data["last_agent"]
		del stock_data["error"]

	return stock_data


# Function to be ran asynchronously
def run_crew(ref, stock):
	print("[THREAD] Started!")
	try:
		# Import crew and instantiate
		from agents.src.act_agents.crew import ActAgentsCrew
		crew = ActAgentsCrew()

		tasks = [
			f"Researching {stock}...",
			"Calculating accounting ratios...",
			f"Analysing {stock}, making recommendations...",
			"Formatting output..."
		]

		# Track progress
		progress = 0

		def update_progress():
			ref.update({"current_task": tasks[progress]})

		update_progress()

		# Register a callback function
		def task_callback(output):
			nonlocal progress
			progress += 1
			print(f"[CREW] {progress}/4 tasks complete")
			if progress < len(tasks):
				update_progress()
		crew.set_task_callback(task_callback)
		
		print("[CREW] Starting...")
		# Run the crew to generate a report
		report = crew.crew().kickoff(inputs = {
			"stock": stock
		})

		ref.update({
			"state": "finished",
			"report": str(report),
			"current_task": None
		})

	except Exception as e:
		print(f"[THREAD] Error: {e}")
		ref.update({
			"state": "error",
			"error": str(e),
			"current_task": None
		})