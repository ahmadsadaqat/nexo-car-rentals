"""Vehicle Odometer Log Service — manages odometer tracking for fleet vehicles."""

import frappe
from frappe import _
from typing import Optional

from nexorentals.car_rental.services.base import BaseService, require_permission
from nexorentals.car_rental.repositories.vehicle_odometer_log_repository import VehicleOdometerLogRepository
from nexorentals.car_rental.repositories.vehicle_repository import VehicleRepository


class VehicleOdometerLogService(BaseService):
	"""
	Manages odometer readings for all fleet vehicles.

	Responsibilities:
	    - Create log entries at trip start/end and on manual updates
	    - Update vehicle.current_odometer on every log entry
	    - Validate new readings are never less than current
	"""

	def __init__(self, user: Optional[str] = None) -> None:
		super().__init__(user)
		self.repo = VehicleOdometerLogRepository()
		self.vehicle_repo = VehicleRepository()

	@require_permission("Vehicle Odometer Log", "create")
	def log_reading(
		self,
		vehicle: str,
		reading: float,
		log_type: str,
		reservation: Optional[str] = None,
		notes: Optional[str] = None,
	) -> object:
		"""
		Create a new odometer log entry and update vehicle's current odometer.

		Args:
		    vehicle: Vehicle name (license plate)
		    reading: New odometer reading in km
		    log_type: One of 'Trip Start', 'Trip End', 'Manual Update'
		    reservation: Linked Car Reservation name (optional)
		    notes: Optional notes

		Raises:
		    frappe.ValidationError: If reading is less than vehicle's current odometer
		"""
		current = frappe.db.get_value("Vehicle", vehicle, "current_odometer") or 0
		if reading < current:
			frappe.throw(
				_("Odometer reading ({0} km) cannot be less than current vehicle reading ({1} km)").format(
					reading, current
				)
			)
		log = self.repo.create_log(vehicle, reading, log_type, reservation, notes)
		self.vehicle_repo.update_odometer(vehicle, reading)
		return log

	@require_permission("Vehicle Odometer Log", "read")
	def get_vehicle_history(self, vehicle: str, limit: int = 20) -> list[dict]:
		"""Return odometer history for a vehicle, newest first."""
		return self.repo.get_history(vehicle, limit)
