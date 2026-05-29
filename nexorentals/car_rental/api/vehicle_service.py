"""
Vehicle Service API

Endpoints:
    GET  /api/method/nexorentals.car_rental.api.vehicle_service.get_service_history
    GET  /api/method/nexorentals.car_rental.api.vehicle_service.get_pending_services

Authentication:
    Token: Authorization: token api_key:api_secret
    Session: Cookie-based after desk login
"""

import frappe
from frappe import _
from typing import Optional

from nexorentals.car_rental.repositories.vehicle_service_repository import VehicleServiceRepository


def _check_permission(doctype: str, ptype: str = "read") -> None:
	if not frappe.has_permission(doctype, ptype):
		frappe.throw(
			_("Permission denied: {0} on {1}").format(ptype, doctype),
			frappe.PermissionError,
		)


@frappe.whitelist()
def get_service_history(vehicle: str, limit: int = 20) -> dict:
	"""
	Return service history for a vehicle.

	Args:
	    vehicle: Vehicle name
	    limit: Max records to return (default 20)

	Returns:
	    List of service records
	"""
	_check_permission("Vehicle Service", "read")
	repo = VehicleServiceRepository()
	records = repo.get_by_vehicle(vehicle, limit=int(limit))
	return {"success": True, "data": records, "count": len(records)}


@frappe.whitelist()
def get_pending_services(vehicle: Optional[str] = None) -> dict:
	"""
	Return all Scheduled or In Progress service records.

	Args:
	    vehicle: Optional vehicle filter

	Returns:
	    List of pending service records
	"""
	_check_permission("Vehicle Service", "read")
	repo = VehicleServiceRepository()
	statuses = ["Scheduled", "In Progress"]
	if vehicle:
		records = repo.get_pending_for_vehicle(vehicle)
	else:
		records = repo.get_by_status(statuses)
	return {"success": True, "data": records, "count": len(records)}
