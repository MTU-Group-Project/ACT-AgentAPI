from firebase_admin import db

import status

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

	free_mode = False

	# Default state
	if "state" not in stock_data:
		stock_data["state"] = "empty"
	if "free_mode" not in stock_data:
		stock_data["free_mode"] = free_mode
	if stock_data["state"] == "finished" and free_mode != stock_data["free_mode"]:
		stock_data = {
			"state": "empty"
		}

	# If an error occured previously, clear it from the database
	if "error" in stock_data:
		ref.update({"error": None})
		return "Error: " + stock_data["error"]

	# If report does not exist, call the crew to generate one
	if "report" not in stock_data and stock_data["state"] != "generating":
		# Clear any previous stock data
		stock_data["current_task"] = None
		stock_data["error"] = None
		del stock_data["current_task"]
		del stock_data["error"]
		
		# Set state to "generating"
		stock_data["state"] = "generating"
		
		ref.update(stock_data)

		try:
			# Import crew and instantiate
			print("[CREW] Importing...")
			from agents.src.act_agents.crew import ActAgentsCrew
			print("[CREW] Instantiating...")
			crew = ActAgentsCrew()

			# Track progress
			progress = 0
			tasks = [
				f"Researching {stock}...",
				"Calculating accounting ratios...",
				f"Analysing {stock}, making recommendations...",
				"Formatting output..."
			]

			def update_progress():
				current_task = tasks[progress]
				print(f"[CREW] {current_task}")
				stock_data["current_task"] = current_task
				ref.update(stock_data)

			update_progress()

			# Register a callback function for the crew
			def task_callback(output):
				nonlocal progress
				progress += 1
				print(f"[CREW] {progress}/4 tasks complete")
				if progress < len(tasks):
					update_progress()
			crew.set_task_callback(task_callback)
			
			free_mode_message = "The user has not purchased the premium version this service, and is using the free tier, therefore limit your report to only 4 short sentences and include a note informing the user of this restriction."
			print("[CREW] Starting...")
			# Run the crew to generate a report
			report = crew.crew().kickoff(inputs = {
				"stock": stock,
				"mode": free_mode_message if free_mode else ""
			})

			stock_data["state"] = "finished"
			stock_data["report"] = str(report)
			if free_mode:
				stock_data["free_mode"] = True
			stock_data["current_task"] = None

		except Exception as e:
			print(f"[CREW] Error: {e}")
			stock_data["state"] = "error"
			stock_data["error"] = str(e)
			stock_data["current_task"] = None

		ref.update(stock_data)

	return stock_data