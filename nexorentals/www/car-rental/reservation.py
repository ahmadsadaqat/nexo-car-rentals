import frappe

login_required = True


def get_context(context):
	context.title = "Reservation Detail"
	context.no_cache = 1

	name = frappe.form_dict.get("name", "")
	if not name:
		frappe.local.flags.redirect_location = "/car-rental/my-reservations"
		raise frappe.Redirect

	res = frappe.db.get_value(
		"Car Reservation",
		name,
		[
			"name", "status", "customer", "customer_name", "vehicle", "vehicle_name",
			"driver", "trip_start_date", "trip_end_date", "total_days",
			"start_odometer", "end_odometer", "trip_km", "estimated_km",
			"with_driver", "base_amount", "km_charges", "driver_charges",
			"security_deposit", "total_amount", "booking_date", "notes",
			"rate_card",
		],
		as_dict=True,
	)

	if not res:
		frappe.throw(frappe._("Reservation not found"), frappe.DoesNotExistError)

	# Ensure this reservation belongs to the logged-in customer or is in the guest's session cache
	customer = _get_customer_for_user(frappe.session.user)
	allowed_guest = False
	if frappe.session.user == "Guest":
		cache_key = f"guest_reservations:{frappe.session.sid}"
		allowed_reservations = frappe.cache.get_value(cache_key) or []
		if name in allowed_reservations:
			allowed_guest = True

	if not allowed_guest and res.customer != customer:
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)

	context.res        = res
	context.can_cancel = res.status == "Draft"


def _get_customer_for_user(user: str):
	contact = frappe.db.get_value("Contact", {"email_id": user}, "name")
	if not contact:
		return None
	return frappe.db.get_value(
		"Dynamic Link",
		{"link_doctype": "Customer", "parenttype": "Contact", "parent": contact},
		"link_name",
	)
