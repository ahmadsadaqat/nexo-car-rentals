import frappe
from nexorentals.car_rental.repositories.base import BaseRepository


class VehicleDocumentRepository(BaseRepository):
	doctype = "Vehicle Document"

	def get_by_vehicle(self, vehicle: str, limit: int = 20) -> list[dict]:
		return self.get_list(
			filters={"vehicle": vehicle},
			fields=["name", "document_type", "document_number", "expiry_date", "status"],
			order_by="expiry_date asc",
			limit=limit,
		)

	def get_expiring_soon(self, days: int = 30) -> list[dict]:
		from frappe.utils import add_days, today
		cutoff = add_days(today(), days)
		return frappe.get_all(
			"Vehicle Document",
			filters=[
				["status", "=", "Valid"],
				["expiry_date", "<=", cutoff],
			],
			fields=["name", "vehicle", "vehicle_name", "document_type", "expiry_date"],
			order_by="expiry_date asc",
		)

	def get_overdue(self) -> list[dict]:
		from frappe.utils import today
		return frappe.get_all(
			"Vehicle Document",
			filters=[
				["status", "=", "Valid"],
				["expiry_date", "<", today()],
			],
			fields=["name", "vehicle", "document_type", "expiry_date"],
		)
