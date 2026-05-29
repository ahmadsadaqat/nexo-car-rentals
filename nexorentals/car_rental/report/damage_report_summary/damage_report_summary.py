import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "name",                  "label": _("Report ID"),        "fieldtype": "Link",     "options": "Damage Report", "width": 140},
		{"fieldname": "vehicle_name",          "label": _("Vehicle"),          "fieldtype": "Data",     "width": 150},
		{"fieldname": "report_date",           "label": _("Report Date"),      "fieldtype": "Date",     "width": 110},
		{"fieldname": "damage_type",           "label": _("Damage Type"),      "fieldtype": "Data",     "width": 130},
		{"fieldname": "severity",              "label": _("Severity"),         "fieldtype": "Data",     "width": 90},
		{"fieldname": "status",                "label": _("Status"),           "fieldtype": "Data",     "width": 130},
		{"fieldname": "estimated_repair_cost", "label": _("Est. Cost"),        "fieldtype": "Currency", "width": 110},
		{"fieldname": "actual_repair_cost",    "label": _("Actual Cost"),      "fieldtype": "Currency", "width": 110},
		{"fieldname": "repair_vendor",         "label": _("Vendor"),           "fieldtype": "Data",     "width": 130},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("from_date"):
		conditions.append("report_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("report_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]
	if filters.get("vehicle"):
		conditions.append("vehicle = %(vehicle)s")
		values["vehicle"] = filters["vehicle"]

	where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

	return frappe.db.sql(f"""
		SELECT name, vehicle_name, report_date, damage_type, severity,
		       status, estimated_repair_cost, actual_repair_cost, repair_vendor
		FROM `tabDamage Report`
		{where}
		ORDER BY report_date DESC
	""", values, as_dict=True)
