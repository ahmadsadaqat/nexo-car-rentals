import frappe


def get_context(context):
	context.title = "Car Rental Portal"
	context.no_cache = 1

	context.categories = frappe.get_all(
		"Vehicle Category",
		fields=["name", "category_name", "description"],
		order_by="category_name asc",
	)

	context.stats = _get_fleet_stats()
	context.is_guest = frappe.session.user == "Guest"


def _get_fleet_stats():
	total     = frappe.db.count("Vehicle", {"registration_stage": "Active"})
	available = frappe.db.count("Vehicle", {"registration_stage": "Active", "status": "Available"})
	categories = frappe.db.count("Vehicle Category")
	return {"total": total, "available": available, "categories": categories}
