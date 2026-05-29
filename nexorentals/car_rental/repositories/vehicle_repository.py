import frappe
from nexorentals.car_rental.repositories.base import BaseRepository


class VehicleRepository(BaseRepository):
	doctype = "Vehicle"

	def get_available(self, vehicle_category: str | None = None) -> list[dict]:
		filters = {"status": "Available", "registration_stage": "Active"}
		if vehicle_category:
			filters["vehicle_category"] = vehicle_category
		return self.get_list(
			filters=filters,
			fields=["name", "vehicle_name", "license_plate", "vehicle_category", "current_odometer", "color"],
			order_by="vehicle_name asc",
			limit=100,
		)

	def get_by_status(self, status: str) -> list[dict]:
		return self.get_list(
			filters={"status": status},
			fields=["name", "vehicle_name", "license_plate", "status", "registration_stage"],
			order_by="vehicle_name asc",
			limit=100,
		)

	def update_odometer(self, name: str, new_reading: float) -> None:
		from frappe.utils import now_datetime
		frappe.db.set_value("Vehicle", name, {
			"current_odometer": new_reading,
			"last_odometer_update": now_datetime(),
		})

	def set_status(self, name: str, status: str) -> None:
		frappe.db.set_value("Vehicle", name, "status", status)
