import frappe

login_required = True


def get_context(context):
	context.title = "Book a Vehicle"
	context.no_cache = 1
	context.is_guest = frappe.session.user == "Guest"

	vehicle_name = frappe.form_dict.get("vehicle", "")
	if not vehicle_name:
		frappe.local.flags.redirect_location = "/car-rental/vehicles"
		raise frappe.Redirect

	vehicle = frappe.db.get_value(
		"Vehicle",
		vehicle_name,
		["name", "vehicle_name", "vehicle_category", "company_make", "model",
		 "model_year", "fuel_type", "seats", "transmission", "image", "status"],
		as_dict=True,
	)

	if not vehicle:
		frappe.throw(frappe._("Vehicle not found"), frappe.DoesNotExistError)

	if vehicle.status != "Available":
		context.vehicle_unavailable = True

	# Get active rate card for this vehicle's category
	rate_card = frappe.db.get_value(
		"Rate Card",
		{"vehicle_category": vehicle.vehicle_category, "is_active": 1},
		["name", "daily_rate", "per_km_rate", "minimum_km_per_day",
		 "security_deposit", "driver_charges_per_day"],
		as_dict=True,
	)

	context.vehicle   = vehicle
	context.rate_card = rate_card
	context.today     = frappe.utils.today()
	context.tomorrow  = frappe.utils.add_days(frappe.utils.today(), 1)
