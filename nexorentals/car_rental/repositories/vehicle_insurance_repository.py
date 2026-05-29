import frappe
from nexorentals.car_rental.repositories.base import BaseRepository


class VehicleInsuranceRepository(BaseRepository):
	doctype = "Vehicle Insurance"

	def get_active_for_vehicle(self, vehicle: str) -> list[dict]:
		return frappe.get_all(
			"Vehicle Insurance",
			filters={"vehicle": vehicle, "status": "Active"},
			fields=["name", "insurance_company", "policy_number", "insurance_type", "end_date"],
		)

	def get_expiring_soon(self, days: int = 30) -> list[dict]:
		from frappe.utils import add_days, today
		cutoff = add_days(today(), days)
		return frappe.get_all(
			"Vehicle Insurance",
			filters=[
				["status", "=", "Active"],
				["end_date", "<=", cutoff],
			],
			fields=["name", "vehicle", "vehicle_name", "insurance_company", "end_date"],
			order_by="end_date asc",
		)

	def get_by_vehicle(self, vehicle: str, limit: int = 20) -> list[dict]:
		return self.get_list(
			filters={"vehicle": vehicle},
			fields=["name", "insurance_company", "policy_number", "insurance_type", "start_date", "end_date", "status", "premium_amount"],
			order_by="end_date desc",
			limit=limit,
		)
