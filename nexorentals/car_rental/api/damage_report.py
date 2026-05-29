"""
Damage Report API

Endpoints:
    GET  /api/method/nexorentals.car_rental.api.damage_report.get_open_reports
    GET  /api/method/nexorentals.car_rental.api.damage_report.get_damage_history

Authentication:
    Token: Authorization: token api_key:api_secret
    Session: Cookie-based after desk login
"""

import frappe
from frappe import _
from typing import Optional

from nexorentals.car_rental.repositories.damage_report_repository import DamageReportRepository


def _check_permission(doctype: str, ptype: str = "read") -> None:
	if not frappe.has_permission(doctype, ptype):
		frappe.throw(
			_("Permission denied: {0} on {1}").format(ptype, doctype),
			frappe.PermissionError,
		)


@frappe.whitelist()
def get_open_reports() -> dict:
	"""
	Return all non-closed damage reports.

	Returns:
	    List of open/in-progress damage reports
	"""
	_check_permission("Damage Report", "read")
	repo = DamageReportRepository()
	records = repo.get_open_reports()
	return {"success": True, "data": records, "count": len(records)}


@frappe.whitelist()
def get_damage_history(vehicle: str, limit: int = 20) -> dict:
	"""
	Return damage report history for a vehicle.

	Args:
	    vehicle: Vehicle name
	    limit: Max records to return (default 20)

	Returns:
	    List of damage reports sorted by report_date DESC
	"""
	_check_permission("Damage Report", "read")
	repo = DamageReportRepository()
	records = repo.get_by_vehicle(vehicle, limit=int(limit))
	return {"success": True, "data": records, "count": len(records)}
