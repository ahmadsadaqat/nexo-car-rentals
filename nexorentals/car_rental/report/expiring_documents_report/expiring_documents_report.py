import frappe
from frappe import _
from frappe.utils import add_days, today, date_diff, getdate


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "record_type",  "label": _("Type"),          "fieldtype": "Data",  "width": 110},
		{"fieldname": "name",         "label": _("Record ID"),      "fieldtype": "Data",  "width": 150},
		{"fieldname": "vehicle",      "label": _("Vehicle"),        "fieldtype": "Link",  "options": "Vehicle", "width": 120},
		{"fieldname": "vehicle_name", "label": _("Vehicle Name"),   "fieldtype": "Data",  "width": 150},
		{"fieldname": "doc_type",     "label": _("Document Type"),  "fieldtype": "Data",  "width": 160},
		{"fieldname": "expiry_date",  "label": _("Expiry Date"),    "fieldtype": "Date",  "width": 110},
		{"fieldname": "days_left",    "label": _("Days Left"),      "fieldtype": "Int",   "width": 90},
		{"fieldname": "status",       "label": _("Status"),         "fieldtype": "Data",  "width": 90},
	]


def get_data(filters):
	days_ahead = int(filters.get("days_ahead") or 60)
	cutoff = add_days(today(), days_ahead)
	today_date = today()

	rows = []

	# Vehicle Documents
	docs = frappe.get_all(
		"Vehicle Document",
		filters=[["status", "in", ["Valid", "Expired"]], ["expiry_date", "<=", cutoff]],
		fields=["name", "vehicle", "vehicle_name", "document_type", "expiry_date", "status"],
		order_by="expiry_date asc",
	)
	for d in docs:
		days_left = date_diff(d.expiry_date, today_date)
		rows.append({
			"record_type": "Document",
			"name":         d.name,
			"vehicle":      d.vehicle,
			"vehicle_name": d.vehicle_name,
			"doc_type":     d.document_type,
			"expiry_date":  d.expiry_date,
			"days_left":    days_left,
			"status":       d.status,
		})

	# Vehicle Insurance
	policies = frappe.get_all(
		"Vehicle Insurance",
		filters=[["status", "in", ["Active", "Expired"]], ["end_date", "<=", cutoff]],
		fields=["name", "vehicle", "vehicle_name", "insurance_type", "end_date", "status"],
		order_by="end_date asc",
	)
	for p in policies:
		days_left = date_diff(p.end_date, today_date)
		rows.append({
			"record_type": "Insurance",
			"name":         p.name,
			"vehicle":      p.vehicle,
			"vehicle_name": p.vehicle_name,
			"doc_type":     p.insurance_type,
			"expiry_date":  p.end_date,
			"days_left":    days_left,
			"status":       p.status,
		})

	rows.sort(key=lambda r: (r["expiry_date"] or "9999-99-99"))
	return rows
