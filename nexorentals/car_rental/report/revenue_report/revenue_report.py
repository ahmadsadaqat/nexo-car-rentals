import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "period",          "label": _("Period"),          "fieldtype": "Data",     "width": 120},
		{"fieldname": "bookings",        "label": _("Bookings"),        "fieldtype": "Int",      "width": 90},
		{"fieldname": "total_days",      "label": _("Total Days"),      "fieldtype": "Int",      "width": 90},
		{"fieldname": "base_amount",     "label": _("Base Amount"),     "fieldtype": "Currency", "width": 130},
		{"fieldname": "km_charges",      "label": _("KM Charges"),      "fieldtype": "Currency", "width": 120},
		{"fieldname": "driver_charges",  "label": _("Driver Charges"),  "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_revenue",   "label": _("Total Revenue"),   "fieldtype": "Currency", "width": 130},
	]


def get_data(filters):
	conditions = ["status IN ('Completed', 'On Trip')"]
	values = {}

	if filters.get("from_date"):
		conditions.append("trip_start_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("trip_start_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("vehicle_category"):
		conditions.append("vehicle_category = %(vehicle_category)s")
		values["vehicle_category"] = filters["vehicle_category"]

	group_by = "DATE_FORMAT(trip_start_date, '%%Y-%%m')"
	period_label = "DATE_FORMAT(trip_start_date, '%%b %%Y')"

	where = "WHERE " + " AND ".join(conditions)

	return frappe.db.sql(f"""
		SELECT
			{period_label}            AS period,
			COUNT(name)               AS bookings,
			SUM(total_days)           AS total_days,
			SUM(base_amount)          AS base_amount,
			SUM(km_charges)           AS km_charges,
			SUM(driver_charges)       AS driver_charges,
			SUM(total_amount)         AS total_revenue
		FROM `tabCar Reservation`
		{where}
		GROUP BY {group_by}
		ORDER BY MIN(trip_start_date) ASC
	""", values, as_dict=True)
