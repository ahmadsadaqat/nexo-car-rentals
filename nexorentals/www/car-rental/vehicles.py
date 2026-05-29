import frappe


def get_context(context):
	context.title = "Available Vehicles"
	context.no_cache = 1

	category      = frappe.form_dict.get("category", "")
	available_only = frappe.form_dict.get("available_only", "1")

	context.selected_category = category
	context.available_only    = available_only

	context.categories = frappe.get_all(
		"Vehicle Category",
		fields=["name", "category_name"],
		order_by="category_name asc",
	)

	filters = {"registration_stage": "Active"}
	if category:
		filters["vehicle_category"] = category
	if available_only != "0":
		filters["status"] = "Available"

	vehicles = frappe.get_all(
		"Vehicle",
		filters=filters,
		fields=[
			"name", "vehicle_name", "vehicle_category",
			"company_make", "model", "model_year",
			"fuel_type", "seats", "transmission", "color", "image", "status",
		],
		order_by="vehicle_name asc",
	)

	# Attach daily rate from the matching active rate card
	rate_map = _build_rate_map()
	for v in vehicles:
		v["daily_rate"] = rate_map.get(v["vehicle_category"], 0)

	context.vehicles = vehicles
	context.total    = len(vehicles)


def _build_rate_map():
	"""Return {vehicle_category: daily_rate} from active rate cards."""
	rate_cards = frappe.get_all(
		"Rate Card",
		filters={"is_active": 1},
		fields=["vehicle_category", "daily_rate"],
	)
	return {rc["vehicle_category"]: rc["daily_rate"] for rc in rate_cards}
