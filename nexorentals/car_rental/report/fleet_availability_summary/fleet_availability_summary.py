import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "name",             "label": _("Vehicle ID"),       "fieldtype": "Link",     "options": "Vehicle", "width": 120},
		{"fieldname": "vehicle_name",     "label": _("Vehicle Name"),     "fieldtype": "Data",     "width": 160},
		{"fieldname": "vehicle_category", "label": _("Category"),         "fieldtype": "Link",     "options": "Vehicle Category", "width": 130},
		{"fieldname": "company_make",     "label": _("Make"),             "fieldtype": "Data",     "width": 100},
		{"fieldname": "model",            "label": _("Model"),            "fieldtype": "Data",     "width": 100},
		{"fieldname": "status",           "label": _("Status"),           "fieldtype": "Data",     "width": 130},
		{"fieldname": "fuel_type",        "label": _("Fuel Type"),        "fieldtype": "Data",     "width": 100},
		{"fieldname": "seats",            "label": _("Seats"),            "fieldtype": "Int",      "width": 70},
		{"fieldname": "current_odometer", "label": _("Odometer (km)"),    "fieldtype": "Float",    "width": 120},
		{"fieldname": "registration_stage","label": _("Reg. Stage"),      "fieldtype": "Data",     "width": 110},
	]


def get_data(filters):
	conditions = {"registration_stage": "Active"}
	if filters.get("vehicle_category"):
		conditions["vehicle_category"] = filters["vehicle_category"]
	if filters.get("status"):
		conditions["status"] = filters["status"]

	return frappe.get_all(
		"Vehicle",
		filters=conditions,
		fields=[
			"name", "vehicle_name", "vehicle_category",
			"company_make", "model", "status",
			"fuel_type", "seats", "current_odometer", "registration_stage",
		],
		order_by="status asc, vehicle_name asc",
	)
