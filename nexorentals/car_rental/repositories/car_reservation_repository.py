import frappe
from nexorentals.car_rental.repositories.base import BaseRepository


class CarReservationRepository(BaseRepository):
	doctype = "Car Reservation"

	def get_by_status(self, status: str | list[str], limit: int = 50) -> list[dict]:
		filters = {"status": ["in", status] if isinstance(status, list) else status}
		return self.get_list(
			filters=filters,
			fields=[
				"name", "status", "customer", "customer_name", "vehicle",
				"vehicle_name", "driver", "trip_start_date", "trip_end_date", "total_amount",
			],
			order_by="booking_date desc",
			limit=limit,
		)

	def get_active_for_vehicle(self, vehicle: str) -> list[dict]:
		return frappe.get_all(
			"Car Reservation",
			filters={"vehicle": vehicle, "status": ["in", ["Approved", "On Trip"]]},
			fields=["name", "status", "trip_start_date", "trip_end_date"],
		)

	def is_vehicle_booked_in_period(self, vehicle: str, start_date: str, end_date: str, exclude: str = "") -> bool:
		filters = [
			["vehicle", "=", vehicle],
			["status", "in", ["Approved", "On Trip", "Pending Approval"]],
			["trip_start_date", "<=", end_date],
			["trip_end_date", ">=", start_date],
		]
		if exclude:
			filters.append(["name", "!=", exclude])
		return bool(frappe.get_all("Car Reservation", filters=filters, fields=["name"], limit=1))

	def get_dashboard_counts(self) -> dict:
		statuses = ["Draft", "Pending Approval", "Approved", "On Trip", "Completed", "Cancelled"]
		return {s: self.get_count({"status": s}) for s in statuses}
