import frappe
from nexorentals.car_rental.repositories.base import BaseRepository


class DriverRepository(BaseRepository):
	doctype = "Driver"

	def get_active_drivers(self) -> list[dict]:
		return self.get_list(
			filters={"status": "Active"},
			fields=["name", "driver_name", "license_number", "license_expiry", "contact_number"],
			order_by="driver_name asc",
			limit=100,
		)

	def get_expiring_licenses(self, days: int = 30) -> list[dict]:
		from frappe.utils import add_days, today
		expiry_threshold = add_days(today(), days)
		return frappe.get_all(
			"Driver",
			filters={
				"status": "Active",
				"license_expiry": ["<=", expiry_threshold],
			},
			fields=["name", "driver_name", "license_number", "license_expiry"],
		)
