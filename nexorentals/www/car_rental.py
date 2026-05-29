import frappe


def get_context(context):
	context.title = "Car Rental Portal"
	context.no_cache = 1
	context.stats = {"total": 0, "available": 0, "categories": 0}
	context.categories = []
	context.is_guest = frappe.session.user == "Guest"

	context.categories = frappe.get_all(
		"Vehicle Category",
		fields=["name", "category_name", "description"],
		order_by="category_name asc",
		ignore_permissions=True,
	)

	context.stats = _get_fleet_stats()


def _get_fleet_stats():
	total = frappe.db.count("Vehicle", {"status": "Available"})
	available = frappe.db.count("Vehicle", {"status": "Available"})
	categories = frappe.db.count("Vehicle Category")
	return {"total": total, "available": available, "categories": categories}
