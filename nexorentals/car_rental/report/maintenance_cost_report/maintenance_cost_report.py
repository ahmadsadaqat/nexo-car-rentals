import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "name",            "label": _("Service ID"),      "fieldtype": "Link",     "options": "Vehicle Service", "width": 140},
		{"fieldname": "vehicle_name",    "label": _("Vehicle"),         "fieldtype": "Data",     "width": 150},
		{"fieldname": "service_date",    "label": _("Service Date"),    "fieldtype": "Date",     "width": 110},
		{"fieldname": "service_type",    "label": _("Service Type"),    "fieldtype": "Data",     "width": 150},
		{"fieldname": "status",          "label": _("Status"),          "fieldtype": "Data",     "width": 110},
		{"fieldname": "vendor",          "label": _("Vendor"),          "fieldtype": "Data",     "width": 140},
		{"fieldname": "service_cost",    "label": _("Service Cost"),    "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = {}
	if filters.get("from_date"):
		conditions["service_date"] = [">=", filters["from_date"]]
	if filters.get("vehicle"):
		conditions["vehicle"] = filters["vehicle"]
	if filters.get("service_type"):
		conditions["service_type"] = filters["service_type"]

	# Handle date range properly
	date_cond = []
	values = {}
	if filters.get("from_date"):
		date_cond.append("service_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		date_cond.append("service_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("vehicle"):
		date_cond.append("vehicle = %(vehicle)s")
		values["vehicle"] = filters["vehicle"]
	if filters.get("service_type"):
		date_cond.append("service_type = %(service_type)s")
		values["service_type"] = filters["service_type"]

	where = ("WHERE " + " AND ".join(date_cond)) if date_cond else ""

	return frappe.db.sql(f"""
		SELECT name, vehicle_name, service_date, service_type, status, vendor, service_cost
		FROM `tabVehicle Service`
		{where}
		ORDER BY service_date DESC
	""", values, as_dict=True)
