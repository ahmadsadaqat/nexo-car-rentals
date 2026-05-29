"""
Car Reservation API

Endpoints:
    POST /api/method/nexorentals.car_rental.api.car_reservation.complete_trip
    GET  /api/method/nexorentals.car_rental.api.car_reservation.calculate_cost
    GET  /api/method/nexorentals.car_rental.api.car_reservation.get_available_vehicles
    GET  /api/method/nexorentals.car_rental.api.car_reservation.get_dashboard_stats

Authentication:
    Token: Authorization: token api_key:api_secret
    Session: Cookie-based after desk login
"""

import frappe
from frappe import _
from frappe.utils import cint, flt
from typing import Optional

from nexorentals.car_rental.services.car_reservation_service import CarReservationService
from nexorentals.car_rental.services.vehicle_service import VehicleService


# ─────────────────────────────────────────────────────────────────────────────
# Permission helper
# ─────────────────────────────────────────────────────────────────────────────

def _check_permission(doctype: str, ptype: str = "read") -> None:
	if not frappe.has_permission(doctype, ptype):
		frappe.throw(
			_("Permission denied: {0} on {1}").format(ptype, doctype),
			frappe.PermissionError,
		)


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist(methods=["POST"])
def complete_trip(name: str, end_odometer: float, actual_km: Optional[float] = None) -> dict:
	"""
	Complete an active trip.

	Args:
	    name: Car Reservation name
	    end_odometer: Final odometer reading (km)
	    actual_km: Actual km driven override (optional, defaults to end - start)

	Returns:
	    Updated reservation summary

	Example:
	    POST /api/method/nexorentals.car_rental.api.car_reservation.complete_trip
	    Body: {"name": "NR-RES-2026-0001", "end_odometer": 45200}
	"""
	_check_permission("Car Reservation", "write")

	end_odometer = flt(end_odometer)
	actual_km    = flt(actual_km) if actual_km else None

	svc = CarReservationService()
	svc.complete_trip(name, end_odometer, actual_km)

	return {
		"success": True,
		"message": _("Trip completed successfully"),
		"data": frappe.db.get_value(
			"Car Reservation",
			name,
			["status", "trip_km", "total_amount", "end_odometer"],
			as_dict=True,
		),
	}


@frappe.whitelist(allow_guest=True)
def calculate_cost(
	rate_card: str,
	total_days: int,
	estimated_km: float = 0,
	with_driver: int = 0,
) -> dict:
	"""
	Calculate rental cost for given parameters (used by the form JS).

	Args:
	    rate_card: Rate Card name
	    total_days: Number of rental days
	    estimated_km: Estimated km for the trip
	    with_driver: 1 if driver is included, 0 otherwise

	Returns:
	    Cost breakdown dict
	"""
	if frappe.session.user != "Guest":
		_check_permission("Rate Card", "read")

	total_days   = cint(total_days) or 1
	estimated_km = flt(estimated_km)

	rate = frappe.db.get_value(
		"Rate Card",
		rate_card,
		["daily_rate", "per_km_rate", "minimum_km_per_day", "security_deposit", "driver_charges_per_day"],
		as_dict=True,
	)
	if not rate:
		frappe.throw(_("Rate Card {0} not found").format(rate_card))

	base       = (rate.daily_rate or 0) * total_days
	min_km     = (rate.minimum_km_per_day or 0) * total_days
	extra_km   = max(0, estimated_km - min_km)
	km_charges = extra_km * (rate.per_km_rate or 0)
	drv_charges = (rate.driver_charges_per_day or 0) * total_days if with_driver else 0

	return {
		"base_amount":    base,
		"km_charges":     km_charges,
		"driver_charges": drv_charges,
		"security_deposit": rate.security_deposit or 0,
		"total":          base + km_charges + drv_charges,
	}


@frappe.whitelist()
def get_available_vehicles(vehicle_category: Optional[str] = None) -> dict:
	"""
	Return all vehicles available for new bookings.

	Args:
	    vehicle_category: Optional category filter

	Returns:
	    List of available vehicles with key details
	"""
	_check_permission("Vehicle", "read")
	vehicles = VehicleService().get_available_vehicles(vehicle_category)
	return {"success": True, "data": vehicles, "count": len(vehicles)}


@frappe.whitelist()
def get_dashboard_stats() -> dict:
	"""
	Return reservation and fleet counts for the dashboard.

	Returns:
	    Reservation counts by status + fleet availability summary
	"""
	_check_permission("Car Reservation", "read")
	svc = CarReservationService()
	fleet_svc = VehicleService()
	return {
		"success": True,
		"reservations": svc.repo.get_dashboard_counts(),
		"fleet": fleet_svc.get_fleet_summary(),
	}
