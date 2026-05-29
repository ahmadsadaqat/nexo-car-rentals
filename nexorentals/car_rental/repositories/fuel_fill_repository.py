import frappe
from nexorentals.car_rental.repositories.base import BaseRepository


class FuelFillRepository(BaseRepository):
	doctype = "Fuel Fill"

	def get_by_vehicle(self, vehicle: str, limit: int = 50) -> list[dict]:
		return self.get_list(
			filters={"vehicle": vehicle},
			fields=["name", "fill_date", "liters", "cost_per_liter", "total_cost", "odometer_at_fill", "station_name"],
			order_by="fill_date desc",
			limit=limit,
		)

	def get_by_reservation(self, reservation: str) -> list[dict]:
		return frappe.get_all(
			"Fuel Fill",
			filters={"reservation": reservation},
			fields=["name", "fill_date", "liters", "total_cost"],
		)

	def get_total_cost_for_vehicle(self, vehicle: str, from_date: str = "", to_date: str = "") -> float:
		filters: list = [["vehicle", "=", vehicle]]
		if from_date:
			filters.append(["fill_date", ">=", from_date])
		if to_date:
			filters.append(["fill_date", "<=", to_date])
		result = frappe.db.get_value(
			"Fuel Fill",
			filters,
			"sum(total_cost)",
		)
		return result or 0.0
