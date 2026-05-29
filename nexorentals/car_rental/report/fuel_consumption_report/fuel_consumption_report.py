import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "vehicle",         "label": _("Vehicle"),         "fieldtype": "Link",     "options": "Vehicle", "width": 120},
		{"fieldname": "vehicle_name",    "label": _("Vehicle Name"),    "fieldtype": "Data",     "width": 160},
		{"fieldname": "fuel_type",       "label": _("Fuel Type"),       "fieldtype": "Data",     "width": 100},
		{"fieldname": "fills",           "label": _("Fills"),           "fieldtype": "Int",      "width": 70},
		{"fieldname": "total_liters",    "label": _("Total Liters"),    "fieldtype": "Float",    "width": 110},
		{"fieldname": "total_cost",      "label": _("Total Cost"),      "fieldtype": "Currency", "width": 120},
		{"fieldname": "avg_cost_liter",  "label": _("Avg Cost/Liter"),  "fieldtype": "Currency", "width": 130},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("from_date"):
		conditions.append("fill_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("fill_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("vehicle"):
		conditions.append("vehicle = %(vehicle)s")
		values["vehicle"] = filters["vehicle"]

	where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

	return frappe.db.sql(f"""
		SELECT
			vehicle,
			vehicle_name,
			fuel_type,
			COUNT(name)                    AS fills,
			SUM(liters)                    AS total_liters,
			SUM(total_cost)                AS total_cost,
			ROUND(AVG(cost_per_liter), 3)  AS avg_cost_liter
		FROM `tabFuel Fill`
		{where}
		GROUP BY vehicle
		ORDER BY total_cost DESC
	""", values, as_dict=True)
