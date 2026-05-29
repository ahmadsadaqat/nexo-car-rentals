import frappe
from frappe.utils import now_datetime
from nexorentals.car_rental.repositories.base import BaseRepository


class VehicleOdometerLogRepository(BaseRepository):
	doctype = "Vehicle Odometer Log"

	def create_log(
		self,
		vehicle: str,
		reading: float,
		log_type: str,
		reservation: str | None = None,
		notes: str | None = None,
	) -> object:
		previous = frappe.db.get_value("Vehicle", vehicle, "current_odometer") or 0
		return self.create(
			{
				"vehicle": vehicle,
				"log_date": now_datetime(),
				"odometer_reading": reading,
				"log_type": log_type,
				"reservation": reservation,
				"previous_reading": previous,
				"notes": notes,
			}
		)

	def get_history(self, vehicle: str, limit: int = 20) -> list[dict]:
		return self.get_list(
			filters={"vehicle": vehicle},
			fields=["name", "log_date", "odometer_reading", "log_type", "reservation", "km_difference"],
			order_by="log_date desc",
			limit=limit,
		)
