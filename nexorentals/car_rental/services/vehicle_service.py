"""Vehicle Service — business logic for Vehicle master management."""

import frappe
from frappe import _
from typing import Optional

from nexorentals.car_rental.services.base import BaseService, require_permission, log_operation
from nexorentals.car_rental.repositories.vehicle_repository import VehicleRepository


class VehicleService(BaseService):
	"""
	Handles all business operations for the Vehicle DocType.

	Responsibilities:
	    - Vehicle creation with name auto-generation
	    - Status transitions (Available ↔ Reserved ↔ On Trip ↔ Maintenance)
	    - Odometer validation and updates
	    - Fleet availability queries

	Architecture:
	    Controller → VehicleService → VehicleRepository → Database
	"""

	def __init__(self, user: Optional[str] = None) -> None:
		super().__init__(user)
		self.repo = VehicleRepository()

	@require_permission("Vehicle", "read")
	def get_available_vehicles(self, vehicle_category: Optional[str] = None) -> list[dict]:
		"""Return all vehicles available for booking."""
		return self.repo.get_available(vehicle_category)

	@require_permission("Vehicle", "write")
	@log_operation("update_odometer")
	def update_odometer(self, vehicle_name: str, new_reading: float) -> None:
		"""
		Update vehicle odometer reading.

		Raises:
		    frappe.ValidationError: If new reading is less than current reading.
		"""
		doc = self.repo.get_or_throw(vehicle_name)
		if new_reading < (doc.current_odometer or 0):
			frappe.throw(
				_("New odometer reading ({0} km) cannot be less than current ({1} km)").format(
					new_reading, doc.current_odometer
				)
			)
		self.repo.update_odometer(vehicle_name, new_reading)

	@require_permission("Vehicle", "write")
	def set_status(self, vehicle_name: str, status: str) -> None:
		"""Transition vehicle to a new operational status."""
		valid = {"Available", "Reserved", "On Trip", "Under Maintenance", "Contract Expired", "Retired"}
		if status not in valid:
			frappe.throw(_("Invalid vehicle status: {0}").format(status))
		self.repo.set_status(vehicle_name, status)

	def get_fleet_summary(self) -> dict:
		"""Return counts by status for the dashboard."""
		statuses = ["Available", "Reserved", "On Trip", "Under Maintenance", "Contract Expired", "Retired"]
		return {s: self.repo.get_count({"status": s}) for s in statuses}
