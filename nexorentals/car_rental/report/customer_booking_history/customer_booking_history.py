import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "name",            "label": _("Booking ID"),    "fieldtype": "Link",     "options": "Car Reservation", "width": 150},
		{"fieldname": "booking_date",    "label": _("Booked On"),     "fieldtype": "Date",     "width": 100},
		{"fieldname": "customer_name",   "label": _("Customer"),      "fieldtype": "Data",     "width": 160},
		{"fieldname": "vehicle_name",    "label": _("Vehicle"),       "fieldtype": "Data",     "width": 150},
		{"fieldname": "vehicle_category","label": _("Category"),      "fieldtype": "Data",     "width": 130},
		{"fieldname": "trip_start_date", "label": _("Start Date"),    "fieldtype": "Date",     "width": 100},
		{"fieldname": "trip_end_date",   "label": _("End Date"),      "fieldtype": "Date",     "width": 100},
		{"fieldname": "total_days",      "label": _("Days"),          "fieldtype": "Int",      "width": 60},
		{"fieldname": "status",          "label": _("Status"),        "fieldtype": "Data",     "width": 120},
		{"fieldname": "total_amount",    "label": _("Total Amount"),  "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("customer"):
		conditions.append("customer = %(customer)s")
		values["customer"] = filters["customer"]
	if filters.get("from_date"):
		conditions.append("booking_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("booking_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]

	where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

	return frappe.db.sql(f"""
		SELECT
			name, booking_date, customer_name, vehicle_name, vehicle_category,
			trip_start_date, trip_end_date, total_days, status, total_amount
		FROM `tabCar Reservation`
		{where}
		ORDER BY booking_date DESC
	""", values, as_dict=True)
