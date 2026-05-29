import frappe
from nexorentals.car_rental.repositories.base import BaseRepository


class DamageReportRepository(BaseRepository):
	doctype = "Damage Report"

	def get_by_vehicle(self, vehicle: str, limit: int = 20) -> list[dict]:
		return self.get_list(
			filters={"vehicle": vehicle},
			fields=["name", "report_date", "damage_type", "severity", "status", "estimated_repair_cost"],
			order_by="report_date desc",
			limit=limit,
		)

	def get_open_reports(self) -> list[dict]:
		return frappe.get_all(
			"Damage Report",
			filters={"status": ["not in", ["Closed"]]},
			fields=["name", "vehicle", "vehicle_name", "damage_type", "severity", "status", "report_date"],
			order_by="report_date desc",
		)

	def get_by_reservation(self, reservation: str) -> list[dict]:
		return frappe.get_all(
			"Damage Report",
			filters={"reservation": reservation},
			fields=["name", "damage_type", "severity", "status", "estimated_repair_cost"],
		)
