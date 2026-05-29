import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "driver",       "label": _("Driver ID"),     "fieldtype": "Link",  "options": "Driver", "width": 120},
		{"fieldname": "driver_name",  "label": _("Driver Name"),   "fieldtype": "Data",  "width": 160},
		{"fieldname": "trips",        "label": _("Trips"),         "fieldtype": "Int",   "width": 80},
		{"fieldname": "total_days",   "label": _("Total Days"),    "fieldtype": "Int",   "width": 100},
		{"fieldname": "total_km",     "label": _("Total KM"),      "fieldtype": "Float", "width": 110},
		{"fieldname": "avg_km_trip",  "label": _("Avg KM / Trip"), "fieldtype": "Float", "width": 120},
	]


def get_data(filters):
	conditions = ["driver IS NOT NULL AND driver != ''", "status IN ('Completed', 'On Trip')"]
	values = {}

	if filters.get("from_date"):
		conditions.append("trip_start_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("trip_end_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("driver"):
		conditions.append("driver = %(driver)s")
		values["driver"] = filters["driver"]

	where = "WHERE " + " AND ".join(conditions)

	return frappe.db.sql(f"""
		SELECT
			driver,
			MAX(driver_name)           AS driver_name,
			COUNT(name)                AS trips,
			SUM(total_days)            AS total_days,
			SUM(trip_km)               AS total_km,
			ROUND(AVG(trip_km), 1)     AS avg_km_trip
		FROM `tabCar Reservation`
		{where}
		GROUP BY driver
		ORDER BY trips DESC
	""", values, as_dict=True)
