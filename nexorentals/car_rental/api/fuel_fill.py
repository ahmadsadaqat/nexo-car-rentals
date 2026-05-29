"""
Fuel Fill API

Endpoints:
    GET  /api/method/nexorentals.car_rental.api.fuel_fill.get_fuel_history
    GET  /api/method/nexorentals.car_rental.api.fuel_fill.get_vehicle_fuel_summary

Authentication:
    Token: Authorization: token api_key:api_secret
    Session: Cookie-based after desk login
"""

import frappe
from frappe import _
from typing import Optional

from nexorentals.car_rental.services.fuel_fill_service import FuelFillService
from nexorentals.car_rental.repositories.fuel_fill_repository import FuelFillRepository


def _check_permission(doctype: str, ptype: str = "read") -> None:
	if not frappe.has_permission(doctype, ptype):
		frappe.throw(
			_("Permission denied: {0} on {1}").format(ptype, doctype),
			frappe.PermissionError,
		)


@frappe.whitelist()
def get_fuel_history(vehicle: str, limit: int = 20) -> dict:
	"""
	Return fuel fill history for a vehicle.

	Args:
	    vehicle: Vehicle name
	    limit: Max records to return (default 20)

	Returns:
	    List of fuel fill records
	"""
	_check_permission("Fuel Fill", "read")
	repo = FuelFillRepository()
	records = repo.get_by_vehicle(vehicle, limit=int(limit))
	return {"success": True, "data": records, "count": len(records)}


@frappe.whitelist()
def get_vehicle_fuel_summary(vehicle: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> dict:
	"""
	Return aggregated fuel statistics for a vehicle.

	Args:
	    vehicle: Vehicle name
	    from_date: Optional start date (YYYY-MM-DD)
	    to_date: Optional end date (YYYY-MM-DD)

	Returns:
	    Total fills, liters, and cost
	"""
	_check_permission("Fuel Fill", "read")
	svc = FuelFillService()
	return {
		"success": True,
		"data": svc.get_vehicle_fuel_summary(vehicle, from_date or "", to_date or ""),
	}
