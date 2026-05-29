"""
Fuel Fill Service

Handles fuel fill record creation and cost calculations.

Architecture:
    FuelFill controller → FuelFillService → Repositories → Database
"""

import frappe
from frappe import _
from frappe.utils import flt
from typing import Optional

from nexorentals.car_rental.services.base import BaseService, require_permission, log_operation
from nexorentals.car_rental.repositories.fuel_fill_repository import FuelFillRepository
from nexorentals.car_rental.repositories.vehicle_repository import VehicleRepository


class FuelFillService(BaseService):
	"""
	Business logic for Fuel Fill records.

	Usage:
	    svc = FuelFillService()
	    summary = svc.get_vehicle_fuel_summary("VH-001")
	"""

	def __init__(self, user: Optional[str] = None) -> None:
		super().__init__(user)
		self.repo   = FuelFillRepository()
		self.v_repo = VehicleRepository()

	@require_permission("Fuel Fill", "read")
	def get_vehicle_fuel_summary(self, vehicle: str, from_date: str = "", to_date: str = "") -> dict:
		"""Return total liters and cost for a vehicle within an optional date range."""
		fills = self.repo.get_by_vehicle(vehicle)
		if from_date or to_date:
			fills = [
				f for f in fills
				if (not from_date or str(f.get("fill_date", "")) >= from_date)
				and (not to_date or str(f.get("fill_date", "")) <= to_date)
			]
		total_liters = sum(flt(f.get("liters", 0)) for f in fills)
		total_cost   = sum(flt(f.get("total_cost", 0)) for f in fills)
		return {
			"vehicle": vehicle,
			"fills": len(fills),
			"total_liters": total_liters,
			"total_cost": total_cost,
		}
