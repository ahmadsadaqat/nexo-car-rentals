"""
Customer Web Portal API

Endpoints:
    POST /api/method/nexorentals.car_rental.api.portal.create_reservation
    GET  /api/method/nexorentals.car_rental.api.portal.get_my_reservations
    POST /api/method/nexorentals.car_rental.api.portal.cancel_my_reservation

Authentication:
    Session: Cookie-based (portal login required for all endpoints)
"""

import frappe
from frappe import _
from frappe.utils import flt, cint, today


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_reservation(
	vehicle: str,
	trip_start_date: str,
	trip_end_date: str,
	with_driver: int = 0,
	estimated_km: float = 0,
	notes: str = "",
	pickup_location: str = None,
	dropoff_location: str = None,
	guest_name: str = None,
	guest_email: str = None,
	guest_phone: str = None,
) -> dict:
	"""
	Create a new Car Reservation from the customer portal.

	Finds or creates the Customer record (including guest profiles),
	validates availability, calculates cost, and saves the Draft reservation.

	Returns:
	    {"success": True, "name": "NR-RES-2026-0001"}
	"""
	if frappe.session.user == "Guest":
		if not guest_name or not guest_email:
			frappe.throw(_("Please provide your name and email address to book a vehicle."))
		customer = _get_or_create_guest_customer(guest_name, guest_email, guest_phone)
	else:
		customer = _get_or_create_customer(frappe.session.user)

	# Validate vehicle is available
	v_status = frappe.db.get_value("Vehicle", vehicle, "status")
	if v_status != "Available":
		frappe.throw(_("Vehicle {0} is not available (status: {1})").format(vehicle, v_status))

	# Validate dates
	if trip_end_date <= trip_start_date:
		frappe.throw(_("End date must be after start date"))

	total_days = _day_diff(trip_start_date, trip_end_date)

	# Get rate card
	vehicle_category = frappe.db.get_value("Vehicle", vehicle, "vehicle_category")
	rate_card = frappe.db.get_value(
		"Rate Card",
		{"vehicle_category": vehicle_category, "is_active": 1},
		"name",
	)

	# Get start odometer
	start_odometer = frappe.db.get_value("Vehicle", vehicle, "current_odometer") or 0

	doc = frappe.get_doc({
		"doctype": "Car Reservation",
		"customer": customer,
		"vehicle": vehicle,
		"trip_start_date": trip_start_date,
		"trip_end_date": trip_end_date,
		"total_days": total_days,
		"with_driver": cint(with_driver),
		"estimated_km": flt(estimated_km),
		"rate_card": rate_card,
		"start_odometer": start_odometer,
		"notes": notes,
		"pickup_location": pickup_location or "Headquarters",
		"dropoff_location": dropoff_location or "Headquarters",
		"status": "Draft",
		"booking_date": today(),
	})

	# Run cost calculation if rate card exists
	if rate_card:
		_fill_costs(doc, rate_card, total_days, flt(estimated_km), cint(with_driver))

	doc.insert(ignore_permissions=True)

	if frappe.session.user == "Guest":
		cache_key = f"guest_reservations:{frappe.session.sid}"
		guest_res = frappe.cache.get_value(cache_key) or []
		guest_res.append(doc.name)
		frappe.cache.set_value(cache_key, guest_res, expires_in_sec=3600)

	frappe.db.commit()

	return {"success": True, "name": doc.name}


@frappe.whitelist()
def get_my_reservations() -> dict:
	"""Return all reservations for the logged-in customer."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please log in"), frappe.PermissionError)

	customer = _get_customer_for_user(frappe.session.user)
	if not customer:
		return {"success": True, "data": [], "count": 0}

	records = frappe.get_all(
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
	return {"success": True, "data": records, "count": len(records)}


@frappe.whitelist(methods=["POST"])
def cancel_my_reservation(name: str) -> dict:
	"""
	Cancel a Draft reservation owned by the logged-in customer.

	Only Draft reservations can be self-cancelled via the portal.
	"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please log in"), frappe.PermissionError)

	customer = _get_customer_for_user(frappe.session.user)
	if not customer:
		frappe.throw(_("No customer record found for your account"), frappe.PermissionError)

	res = frappe.db.get_value("Car Reservation", name, ["customer", "status"], as_dict=True)
	if not res:
		frappe.throw(_("Reservation {0} not found").format(name))
	if res.customer != customer:
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	if res.status != "Draft":
		frappe.throw(_("Only Draft reservations can be cancelled from the portal. Contact us to cancel a confirmed booking."))

	frappe.db.set_value("Car Reservation", name, "status", "Cancelled")
	frappe.db.commit()
	return {"success": True, "message": _("Reservation {0} cancelled").format(name)}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_customer_for_user(user: str):
	"""Return the Customer name linked to this portal user via Contact, or None."""
	contact = frappe.db.get_value("Contact", {"email_id": user}, "name")
	if not contact:
		return None
	return frappe.db.get_value(
		"Dynamic Link",
		{"link_doctype": "Customer", "parenttype": "Contact", "parent": contact},
		"link_name",
	)


def _get_or_create_customer(user: str) -> str:
	"""Return existing Customer for this user, or create one from their profile."""
	existing = _get_customer_for_user(user)
	if existing:
		return existing

	user_doc = frappe.get_doc("User", user)
	full_name = user_doc.full_name or user_doc.email

	# Default customer group — use first non-group entry
	customer_group = (
		frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
		or "All Customer Groups"
	)

	customer = frappe.get_doc({
		"doctype": "Customer",
		"customer_name": full_name,
		"customer_type": "Individual",
		"customer_group": customer_group,
		"territory": "All Territories",
	})
	customer.insert(ignore_permissions=True)

	# Link via Contact so future lookups resolve
	contact = frappe.get_doc({
		"doctype": "Contact",
		"first_name": user_doc.first_name or full_name,
		"last_name": user_doc.last_name or "",
		"email_id": user,
		"links": [{"link_doctype": "Customer", "link_name": customer.name}],
	})
	contact.insert(ignore_permissions=True)
	frappe.db.commit()

	return customer.name


def _get_or_create_guest_customer(name: str, email: str, phone: str = None) -> str:
	"""Return existing Customer for this guest email, or create one."""
	existing = _get_customer_for_user(email)
	if existing:
		return existing

	# Default customer group — use first non-group entry
	customer_group = (
		frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
		or "All Customer Groups"
	)

	customer = frappe.get_doc({
		"doctype": "Customer",
		"customer_name": name,
		"customer_type": "Individual",
		"customer_group": customer_group,
		"territory": "All Territories",
	})
	customer.insert(ignore_permissions=True)

	# Link via Contact so future lookups resolve
	contact_dict = {
		"doctype": "Contact",
		"first_name": name,
		"email_id": email,
		"links": [{"link_doctype": "Customer", "link_name": customer.name}],
	}
	if phone:
		contact_dict["phone"] = phone
		contact_dict["mobile_no"] = phone

	contact = frappe.get_doc(contact_dict)
	contact.insert(ignore_permissions=True)
	frappe.db.commit()

	return customer.name


def _day_diff(start: str, end: str) -> int:
	from frappe.utils import date_diff
	diff = date_diff(end, start)
	return max(1, diff)


def _fill_costs(doc, rate_card: str, total_days: int, estimated_km: float, with_driver: int) -> None:
	rate = frappe.db.get_value(
		"Rate Card",
		rate_card,
		["daily_rate", "per_km_rate", "minimum_km_per_day", "security_deposit", "driver_charges_per_day"],
		as_dict=True,
	)
	if not rate:
		return
	base       = (rate.daily_rate or 0) * total_days
	min_km     = (rate.minimum_km_per_day or 0) * total_days
	extra_km   = max(0, estimated_km - min_km)
	km_charges = extra_km * (rate.per_km_rate or 0)
	drv        = (rate.driver_charges_per_day or 0) * total_days if with_driver else 0

	doc.base_amount      = base
	doc.km_charges       = km_charges
	doc.driver_charges   = drv
	doc.security_deposit = rate.security_deposit or 0
	doc.total_amount     = base + km_charges + drv
