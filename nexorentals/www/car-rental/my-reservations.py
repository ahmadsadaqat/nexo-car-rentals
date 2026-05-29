import frappe

login_required = True


def get_context(context):
	context.title = "My Reservations"
	context.no_cache = 1

	customer = _get_customer_for_user(frappe.session.user)
	context.customer = customer

	if customer:
		context.reservations = frappe.get_all(
			"Car Reservation",
			filters={"customer": customer},
			fields=[
				"name", "status", "vehicle", "vehicle_name",
				"trip_start_date", "trip_end_date", "total_days",
				"total_amount", "booking_date",
			],
			order_by="booking_date desc",
			limit=50,
		)
	else:
		context.reservations = []


def _get_customer_for_user(user: str):
	"""Return the Customer name linked to this portal user, or None."""
	contact = frappe.db.get_value("Contact", {"email_id": user}, "name")
	if not contact:
		return None
	return frappe.db.get_value(
		"Dynamic Link",
		{"link_doctype": "Customer", "parenttype": "Contact", "parent": contact},
		"link_name",
	)
