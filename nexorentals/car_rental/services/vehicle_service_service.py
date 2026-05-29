"""
Vehicle Service Service

Manages maintenance record lifecycle:
  Scheduled → In Progress → Completed

Responsibilities:
    - Status transitions with vehicle status sync
    - Vehicle → Under Maintenance when service starts
    - Vehicle → Available when service completes

Architecture:
    VehicleService controller → VehicleServiceService → Repositories → Database
"""

import frappe
from frappe import _
from typing import Optional

from nexorentals.car_rental.services.base import BaseService, require_permission, log_operation
from nexorentals.car_rental.repositories.vehicle_service_repository import VehicleServiceRepository
from nexorentals.car_rental.repositories.vehicle_repository import VehicleRepository


class VehicleServiceService(BaseService):
	"""
	Lifecycle manager for Vehicle Service (maintenance) records.

	Usage:
	    svc = VehicleServiceService()
	    svc.start_service("NR-SVC-2026-0001")
	    svc.complete_service("NR-SVC-2026-0001")
	"""

	SCHEDULED    = "Scheduled"
	IN_PROGRESS  = "In Progress"
	COMPLETED    = "Completed"

	V_AVAILABLE  = "Available"
	V_MAINTENANCE = "Under Maintenance"

	def __init__(self, user: Optional[str] = None) -> None:
		super().__init__(user)
		self.repo   = VehicleServiceRepository()
		self.v_repo = VehicleRepository()

	# ─────────────────────────────────────────────────────────────────
	# Transition 1: Scheduled → In Progress
	# ─────────────────────────────────────────────────────────────────

	@require_permission("Vehicle Service", "write")
	@log_operation("start_service")
	def start_service(self, name: str) -> None:
		"""Begin a service: vehicle → Under Maintenance."""
		doc = self.repo.get_or_throw(name, for_update=True)
		self._assert_status(doc, self.SCHEDULED, "start service")

		# Capture current odometer if not already set
		if not doc.odometer_at_service:
			current_odo = frappe.db.get_value("Vehicle", doc.vehicle, "current_odometer") or 0
			frappe.db.set_value("Vehicle Service", name, "odometer_at_service", current_odo)

		frappe.db.set_value("Vehicle Service", name, "status", self.IN_PROGRESS)
		self.v_repo.set_status(doc.vehicle, self.V_MAINTENANCE)
		frappe.msgprint(
			_("Service {0} started. Vehicle {1} is now Under Maintenance.").format(name, doc.vehicle),
			indicator="blue",
			alert=True,
		)

	# ─────────────────────────────────────────────────────────────────
	# Transition 2: In Progress → Completed
	# ─────────────────────────────────────────────────────────────────

	@require_permission("Vehicle Service", "write")
	@log_operation("complete_service")
	def complete_service(self, name: str) -> None:
		"""Complete a service: vehicle → Available."""
		doc = self.repo.get_or_throw(name, for_update=True)
		self._assert_status(doc, self.IN_PROGRESS, "complete service")

		frappe.db.set_value("Vehicle Service", name, "status", self.COMPLETED)
		self.v_repo.set_status(doc.vehicle, self.V_AVAILABLE)
		frappe.msgprint(
			_("Service {0} completed. Vehicle {1} is now Available.").format(name, doc.vehicle),
			indicator="green",
			alert=True,
		)

	# ─────────────────────────────────────────────────────────────────
	# Internal helpers
	# ─────────────────────────────────────────────────────────────────

	def _assert_status(self, doc, expected: str, action: str) -> None:
		if doc.status != expected:
			frappe.throw(
				_("Cannot {0}: service record is {1} (expected {2})").format(action, doc.status, expected)
			)
