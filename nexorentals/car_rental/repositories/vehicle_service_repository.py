import frappe
from nexorentals.car_rental.repositories.base import BaseRepository


class VehicleServiceRepository(BaseRepository):
	doctype = "Vehicle Service"

	def get_by_vehicle(self, vehicle: str, limit: int = 50) -> list[dict]:
		return self.get_list(
			filters={"vehicle": vehicle},
			fields=["name", "service_date", "service_type", "status", "service_cost", "vendor"],
			order_by="service_date desc",
			limit=limit,
		)

	def get_by_status(self, status: str | list[str], limit: int = 50) -> list[dict]:
		filters = {"status": ["in", status] if isinstance(status, list) else status}
		return self.get_list(
			filters=filters,
			fields=["name", "vehicle", "vehicle_name", "service_date", "service_type", "status", "service_cost"],
			order_by="service_date desc",
			limit=limit,
		)

	def get_pending_for_vehicle(self, vehicle: str) -> list[dict]:
		return frappe.get_all(
			"Vehicle Service",
			filters={"vehicle": vehicle, "status": ["in", ["Scheduled", "In Progress"]]},
			fields=["name", "status", "service_type", "service_date"],
		)
