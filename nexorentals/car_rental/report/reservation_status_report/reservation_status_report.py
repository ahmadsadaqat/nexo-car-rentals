import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "name",            "label": _("Booking ID"),    "fieldtype": "Link",     "options": "Car Reservation", "width": 150},
		{"fieldname": "booking_date",    "label": _("Booked On"),     "fieldtype": "Date",     "width": 100},
		{"fieldname": "customer_name",   "label": _("Customer"),      "fieldtype": "Data",     "width": 150},
		{"fieldname": "vehicle_name",    "label": _("Vehicle"),       "fieldtype": "Data",     "width": 150},
		{"fieldname": "trip_start_date", "label": _("Start Date"),    "fieldtype": "Date",     "width": 100},
		{"fieldname": "trip_end_date",   "label": _("End Date"),      "fieldtype": "Date",     "width": 100},
		{"fieldname": "total_days",      "label": _("Days"),          "fieldtype": "Int",      "width": 60},
		{"fieldname": "status",          "label": _("Status"),        "fieldtype": "Data",     "width": 120},
		{"fieldname": "base_amount",     "label": _("Base Amount"),   "fieldtype": "Currency", "width": 120},
		{"fieldname": "km_charges",      "label": _("KM Charges"),    "fieldtype": "Currency", "width": 110},
		{"fieldname": "driver_charges",  "label": _("Driver Charges"),"fieldtype": "Currency", "width": 120},
		{"fieldname": "total_amount",    "label": _("Total Amount"),  "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("from_date"):
		conditions.append("trip_start_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("trip_end_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]
	if filters.get("vehicle_category"):
		conditions.append("vehicle_category = %(vehicle_category)s")
		values["vehicle_category"] = filters["vehicle_category"]

	where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

	return frappe.db.sql(f"""
		SELECT
			cr.name, cr.booking_date, cr.customer_name, cr.vehicle_name,
			cr.trip_start_date, cr.trip_end_date, cr.total_days, cr.status,
			cr.base_amount, cr.km_charges, cr.driver_charges, cr.total_amount
		FROM `tabCar Reservation` cr
		{where}
		ORDER BY cr.booking_date DESC
	""", values, as_dict=True)
