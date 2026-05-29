"""
Car Reservation Service

Orchestrates the full booking lifecycle:
  Draft → Pending Approval → Approved → On Trip → Completed / Cancelled

Responsibilities:
    - Status transitions with role enforcement
    - Vehicle availability checks at each stage
    - Odometer capture on trip start/end
    - Cost recalculation on completion
    - Vehicle status synchronization throughout

Architecture:
    CarReservation controller → CarReservationService → Repositories → Database
"""

import frappe
from frappe import _
from frappe.utils import getdate, now_datetime
from typing import Optional

from nexorentals.car_rental.services.base import BaseService, require_permission, log_operation
from nexorentals.car_rental.repositories.car_reservation_repository import CarReservationRepository
from nexorentals.car_rental.repositories.vehicle_repository import VehicleRepository
from nexorentals.car_rental.repositories.vehicle_odometer_log_repository import VehicleOdometerLogRepository


class CarReservationService(BaseService):
	"""
	Full lifecycle manager for Car Reservations.

	Usage:
	    svc = CarReservationService()
	    svc.submit_for_approval("NR-RES-2026-0001")
	    svc.approve("NR-RES-2026-0001")
	    svc.start_trip("NR-RES-2026-0001")
	    svc.complete_trip("NR-RES-2026-0001", end_odometer=45200, actual_km=320)
	"""

	# Status constants
	DRAFT            = "Draft"
	PENDING_APPROVAL = "Pending Approval"
	APPROVED         = "Approved"
	ON_TRIP          = "On Trip"
	COMPLETED        = "Completed"
	CANCELLED        = "Cancelled"

	# Vehicle statuses set by this service
	V_AVAILABLE  = "Available"
	V_RESERVED   = "Reserved"
	V_ON_TRIP    = "On Trip"

	def __init__(self, user: Optional[str] = None) -> None:
		super().__init__(user)
		self.repo      = CarReservationRepository()
		self.v_repo    = VehicleRepository()
		self.odo_repo  = VehicleOdometerLogRepository()

	# ─────────────────────────────────────────────────────────────────────
	# Transition 1: Draft → Pending Approval
	# ─────────────────────────────────────────────────────────────────────

	@require_permission("Car Reservation", "write")
	@log_operation("submit_for_approval")
	def submit_for_approval(self, name: str) -> None:
		"""Submit a Draft reservation for approver review."""
		doc = self.repo.get_or_throw(name, for_update=True)
		self._assert_status(doc, self.DRAFT, "submit for approval")
		self._check_vehicle_available(doc.vehicle, name)
		self._check_overlap(doc)
		frappe.db.set_value("Car Reservation", name, "status", self.PENDING_APPROVAL)
		frappe.msgprint(_("Reservation {0} submitted for approval").format(name), indicator="blue", alert=True)

	# ─────────────────────────────────────────────────────────────────────
	# Transition 2: Pending Approval → Approved
	# ─────────────────────────────────────────────────────────────────────

	@log_operation("approve_reservation")
	def approve(self, name: str) -> None:
		"""Approve a reservation (Car Rental Approver only). Marks vehicle Reserved."""
		self._assert_approver_role()
		doc = self.repo.get_or_throw(name, for_update=True)
		self._assert_status(doc, self.PENDING_APPROVAL, "approve")
		self._check_vehicle_available(doc.vehicle, name)
		frappe.db.set_value("Car Reservation", name, "status", self.APPROVED)
		self.v_repo.set_status(doc.vehicle, self.V_RESERVED)
		frappe.msgprint(_("Reservation {0} approved. Vehicle marked as Reserved.").format(name), indicator="green", alert=True)

	# ─────────────────────────────────────────────────────────────────────
	# Transition 3: Pending Approval → Cancelled (reject)
	# ─────────────────────────────────────────────────────────────────────

	@log_operation("reject_reservation")
	def reject(self, name: str) -> None:
		"""Reject a Pending Approval reservation (approver only)."""
		self._assert_approver_role()
		doc = self.repo.get_or_throw(name, for_update=True)
		self._assert_status(doc, self.PENDING_APPROVAL, "reject")
		frappe.db.set_value("Car Reservation", name, "status", self.CANCELLED)
		frappe.msgprint(_("Reservation {0} rejected.").format(name), indicator="orange", alert=True)

	# ─────────────────────────────────────────────────────────────────────
	# Transition 4: Approved → On Trip
	# ─────────────────────────────────────────────────────────────────────

	@require_permission("Car Reservation", "write")
	@log_operation("start_trip")
	def start_trip(self, name: str) -> None:
		"""Start the trip: capture start odometer, set vehicle On Trip."""
		doc = self.repo.get_or_throw(name, for_update=True)
		self._assert_status(doc, self.APPROVED, "start trip")

		start_odo = frappe.db.get_value("Vehicle", doc.vehicle, "current_odometer") or 0

		frappe.db.set_value("Car Reservation", name, {
			"status": self.ON_TRIP,
			"start_odometer": start_odo,
		})
		self.v_repo.set_status(doc.vehicle, self.V_ON_TRIP)
		self.odo_repo.create_log(doc.vehicle, start_odo, "Trip Start", name, f"Trip started: {name}")
		frappe.msgprint(_("Trip started for reservation {0}.").format(name), indicator="blue", alert=True)

	# ─────────────────────────────────────────────────────────────────────
	# Transition 5: On Trip → Completed
	# ─────────────────────────────────────────────────────────────────────

	@require_permission("Car Reservation", "write")
	@log_operation("complete_trip")
	def complete_trip(self, name: str, end_odometer: float, actual_km: Optional[float] = None) -> None:
		"""
		Complete a trip.

		- Records end odometer and calculates trip_km
		- Updates vehicle.current_odometer
		- Sets vehicle to Available
		- Creates Odometer Log (Trip End)
		- Recalculates rental cost

		Args:
		    name: Car Reservation name
		    end_odometer: Final odometer reading (km)
		    actual_km: Override actual KM; defaults to (end_odometer - start_odometer)
		"""
		doc = self.repo.get_or_throw(name, for_update=True)
		self._assert_status(doc, self.ON_TRIP, "complete trip")

		start_odo = doc.start_odometer or 0
		if end_odometer < start_odo:
			frappe.throw(
				_("End odometer ({0} km) cannot be less than start odometer ({1} km)").format(
					end_odometer, start_odo
				)
			)

		trip_km = end_odometer - start_odo
		km_driven = actual_km if actual_km else trip_km

		# Persist trip measurements
		frappe.db.set_value("Car Reservation", name, {
			"status":        self.COMPLETED,
			"end_odometer":  end_odometer,
			"trip_km":       trip_km,
		})

		# Update vehicle odometer and status
		self.v_repo.update_odometer(doc.vehicle, end_odometer)
		self.v_repo.set_status(doc.vehicle, self.V_AVAILABLE)

		# Create odometer log
		self.odo_repo.create_log(doc.vehicle, end_odometer, "Trip End", name, f"Trip ended: {name}")

		# Recalculate cost with actual km
		self._recalculate_cost(name, doc, km_driven)
		frappe.msgprint(_("Trip {0} completed. Vehicle is now Available.").format(name), indicator="green", alert=True)

	# ─────────────────────────────────────────────────────────────────────
	# Transition 6: Any active state → Cancelled
	# ─────────────────────────────────────────────────────────────────────

	@require_permission("Car Reservation", "write")
	@log_operation("cancel_reservation")
	def cancel_reservation(self, name: str) -> None:
		"""Cancel a reservation in any non-final state and free the vehicle."""
		doc = self.repo.get_or_throw(name, for_update=True)
		if doc.status in (self.COMPLETED, self.CANCELLED):
			frappe.throw(_("Cannot cancel a {0} reservation").format(doc.status))

		frappe.db.set_value("Car Reservation", name, "status", self.CANCELLED)

		# Release vehicle if it was already reserved/on-trip by this booking
		if doc.status in (self.APPROVED, self.ON_TRIP):
			current_v_status = frappe.db.get_value("Vehicle", doc.vehicle, "status")
			if current_v_status in (self.V_RESERVED, self.V_ON_TRIP):
				self.v_repo.set_status(doc.vehicle, self.V_AVAILABLE)

		frappe.msgprint(_("Reservation {0} cancelled.").format(name), indicator="orange", alert=True)

	# ─────────────────────────────────────────────────────────────────────
	# Internal helpers
	# ─────────────────────────────────────────────────────────────────────

	def _assert_status(self, doc, expected: str, action: str) -> None:
		if doc.status != expected:
			frappe.throw(
				_("Cannot {0}: reservation is {1} (expected {2})").format(action, doc.status, expected)
			)

	def _assert_approver_role(self) -> None:
		if not (frappe.user.has_role("Car Rental Approver") or frappe.user.has_role("Fleet Manager")):
			frappe.throw(_("Only Car Rental Approvers can perform this action"), frappe.PermissionError)

	def _check_vehicle_available(self, vehicle: str, exclude_reservation: str = "") -> None:
		blocked = ("Reserved", "On Trip", "Under Maintenance", "Contract Expired", "Retired")
		v_status = frappe.db.get_value("Vehicle", vehicle, "status")
		if v_status in blocked:
			# Allow if the same reservation already holds the vehicle
			if v_status == "Reserved":
				current_holder = frappe.db.get_value(
					"Car Reservation",
					{"vehicle": vehicle, "status": "Approved"},
					"name",
				)
				if current_holder == exclude_reservation:
					return
			frappe.throw(
				_("Vehicle {0} is not available (status: {1})").format(vehicle, v_status)
			)

	def _check_overlap(self, doc) -> None:
		if self.repo.is_vehicle_booked_in_period(
			doc.vehicle, str(doc.trip_start_date), str(doc.trip_end_date), exclude=doc.name
		):
			frappe.throw(
				_("Vehicle {0} already has an active booking in the period {1} – {2}").format(
					doc.vehicle, doc.trip_start_date, doc.trip_end_date
				)
			)

	def _recalculate_cost(self, name: str, doc, km_driven: float) -> None:
		if not doc.rate_card or not doc.total_days:
			return
		rate = frappe.db.get_value(
			"Rate Card",
			doc.rate_card,
			["daily_rate", "per_km_rate", "minimum_km_per_day", "security_deposit", "driver_charges_per_day"],
			as_dict=True,
		)
		if not rate:
			return
		base        = (rate.daily_rate or 0) * doc.total_days
		min_km      = (rate.minimum_km_per_day or 0) * doc.total_days
		extra_km    = max(0, km_driven - min_km)
		km_charges  = extra_km * (rate.per_km_rate or 0)
		drv_charges = (rate.driver_charges_per_day or 0) * doc.total_days if doc.with_driver else 0
		frappe.db.set_value("Car Reservation", name, {
			"base_amount":     base,
			"km_charges":      km_charges,
			"driver_charges":  drv_charges,
			"security_deposit": rate.security_deposit or 0,
			"total_amount":    base + km_charges + drv_charges,
		})
