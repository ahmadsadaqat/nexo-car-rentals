import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "vehicle",         "label": _("Vehicle"),         "fieldtype": "Link",     "options": "Vehicle", "width": 120},
		{"fieldname": "vehicle_name",    "label": _("Vehicle Name"),    "fieldtype": "Data",     "width": 160},
		{"fieldname": "vehicle_category","label": _("Category"),        "fieldtype": "Data",     "width": 130},
		{"fieldname": "trips",           "label": _("Trips"),           "fieldtype": "Int",      "width": 70},
		{"fieldname": "total_days",      "label": _("Total Days"),      "fieldtype": "Int",      "width": 90},
		{"fieldname": "total_km",        "label": _("Total KM"),        "fieldtype": "Float",    "width": 100},
		{"fieldname": "total_revenue",   "label": _("Revenue"),         "fieldtype": "Currency", "width": 120},
		{"fieldname": "avg_km_per_trip", "label": _("Avg KM / Trip"),   "fieldtype": "Float",    "width": 120},
	]


def get_data(filters):
	conditions = ["status IN ('Completed', 'On Trip')"]
	values = {}

	if filters.get("from_date"):
		conditions.append("trip_start_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("trip_end_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("vehicle_category"):
		conditions.append("vehicle_category = %(vehicle_category)s")
		values["vehicle_category"] = filters["vehicle_category"]

	where = "WHERE " + " AND ".join(conditions)

	rows = frappe.db.sql(f"""
		SELECT
			vehicle,
			vehicle_name,
			vehicle_category,
			COUNT(name)               AS trips,
			SUM(total_days)           AS total_days,
			SUM(trip_km)              AS total_km,
			SUM(total_amount)         AS total_revenue,
			ROUND(AVG(trip_km), 1)    AS avg_km_per_trip
		FROM `tabCar Reservation`
		{where}
		GROUP BY vehicle
		ORDER BY trips DESC
	""", values, as_dict=True)

	return rows
