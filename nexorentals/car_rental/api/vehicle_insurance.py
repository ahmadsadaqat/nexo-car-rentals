"""
Vehicle Insurance API

Endpoints:
    GET  /api/method/nexorentals.car_rental.api.vehicle_insurance.get_active_policies
    GET  /api/method/nexorentals.car_rental.api.vehicle_insurance.get_expiring_soon

Authentication:
    Token: Authorization: token api_key:api_secret
    Session: Cookie-based after desk login
"""

import frappe
from frappe import _
from frappe.utils import cint

from nexorentals.car_rental.repositories.vehicle_insurance_repository import VehicleInsuranceRepository


def _check_permission(doctype: str, ptype: str = "read") -> None:
	if not frappe.has_permission(doctype, ptype):
		frappe.throw(
			_("Permission denied: {0} on {1}").format(ptype, doctype),
			frappe.PermissionError,
		)


@frappe.whitelist()
def get_active_policies(vehicle: str = "") -> dict:
	"""
	Return active insurance policies, optionally filtered by vehicle.

	Args:
	    vehicle: Optional vehicle name filter

	Returns:
	    List of active policies
	"""
	_check_permission("Vehicle Insurance", "read")
	repo = VehicleInsuranceRepository()
	if vehicle:
		records = repo.get_active_for_vehicle(vehicle)
	else:
		records = repo.get_list(
			filters={"status": "Active"},
			fields=["name", "vehicle", "vehicle_name", "insurance_company", "policy_number", "end_date"],
			order_by="end_date asc",
		)
	return {"success": True, "data": records, "count": len(records)}


@frappe.whitelist()
def get_expiring_soon(days: int = 30) -> dict:
	"""
	Return active policies expiring within the specified number of days.

	Args:
	    days: Lookahead window in days (default 30)

	Returns:
	    List of expiring policies sorted by end_date ASC
	"""
	_check_permission("Vehicle Insurance", "read")
	repo = VehicleInsuranceRepository()
	records = repo.get_expiring_soon(days=cint(days))
	return {"success": True, "data": records, "count": len(records)}
