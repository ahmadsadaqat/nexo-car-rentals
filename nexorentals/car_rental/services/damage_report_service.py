"""
Damage Report Service

Manages damage assessment and repair lifecycle:
  Open → Under Assessment → Repair Ordered → Repaired → Closed

Responsibilities:
    - Status transitions with vehicle status sync
    - Vehicle → Under Maintenance when repair is ordered
    - Vehicle → Available when repaired

Architecture:
    DamageReport controller → DamageReportService → Repositories → Database
"""

import frappe
from frappe import _
from typing import Optional

from nexorentals.car_rental.services.base import BaseService, require_permission, log_operation
from nexorentals.car_rental.repositories.damage_report_repository import DamageReportRepository
from nexorentals.car_rental.repositories.vehicle_repository import VehicleRepository


class DamageReportService(BaseService):
	"""
	Lifecycle manager for Damage Reports.

	Usage:
	    svc = DamageReportService()
	    svc.start_assessment("NR-DMG-2026-0001")
	    svc.order_repair("NR-DMG-2026-0001")
	    svc.mark_repaired("NR-DMG-2026-0001")
	    svc.close_report("NR-DMG-2026-0001")
	"""

	OPEN             = "Open"
	UNDER_ASSESSMENT = "Under Assessment"
	REPAIR_ORDERED   = "Repair Ordered"
	REPAIRED         = "Repaired"
	CLOSED           = "Closed"

	V_AVAILABLE   = "Available"
	V_MAINTENANCE = "Under Maintenance"

	def __init__(self, user: Optional[str] = None) -> None:
		super().__init__(user)
		self.repo   = DamageReportRepository()
		self.v_repo = VehicleRepository()

	# ─────────────────────────────────────────────────────────────────
	# Transition 1: Open → Under Assessment
	# ─────────────────────────────────────────────────────────────────

	@require_permission("Damage Report", "write")
	@log_operation("start_assessment")
	def start_assessment(self, name: str) -> None:
		"""Begin damage assessment."""
		doc = self.repo.get_or_throw(name, for_update=True)
		self._assert_status(doc, self.OPEN, "start assessment")
		frappe.db.set_value("Damage Report", name, "status", self.UNDER_ASSESSMENT)
		frappe.msgprint(
			_("Damage report {0} is now Under Assessment.").format(name), indicator="blue", alert=True
		)

	# ─────────────────────────────────────────────────────────────────
	# Transition 2: Under Assessment → Repair Ordered
	# ─────────────────────────────────────────────────────────────────

	@require_permission("Damage Report", "write")
	@log_operation("order_repair")
	def order_repair(self, name: str) -> None:
		"""Order repair: vehicle → Under Maintenance."""
		doc = self.repo.get_or_throw(name, for_update=True)
		self._assert_status(doc, self.UNDER_ASSESSMENT, "order repair")
		frappe.db.set_value("Damage Report", name, "status", self.REPAIR_ORDERED)
		self.v_repo.set_status(doc.vehicle, self.V_MAINTENANCE)
		frappe.msgprint(
			_("Repair ordered for {0}. Vehicle {1} is now Under Maintenance.").format(name, doc.vehicle),
			indicator="blue",
			alert=True,
		)

	# ─────────────────────────────────────────────────────────────────
	# Transition 3: Repair Ordered → Repaired
	# ─────────────────────────────────────────────────────────────────

	@require_permission("Damage Report", "write")
	@log_operation("mark_repaired")
	def mark_repaired(self, name: str) -> None:
		"""Mark as repaired: vehicle → Available."""
		doc = self.repo.get_or_throw(name, for_update=True)
		self._assert_status(doc, self.REPAIR_ORDERED, "mark repaired")
		frappe.db.set_value("Damage Report", name, "status", self.REPAIRED)
		self.v_repo.set_status(doc.vehicle, self.V_AVAILABLE)
		frappe.msgprint(
			_("Damage report {0} marked as Repaired. Vehicle {1} is now Available.").format(name, doc.vehicle),
			indicator="green",
			alert=True,
		)

	# ─────────────────────────────────────────────────────────────────
	# Transition 4: Any non-Closed → Closed
	# ─────────────────────────────────────────────────────────────────

	@require_permission("Damage Report", "write")
	@log_operation("close_report")
	def close_report(self, name: str) -> None:
		"""Close a damage report (Fleet Manager only)."""
		self._assert_fleet_manager()
		doc = self.repo.get_or_throw(name, for_update=True)
		if doc.status == self.CLOSED:
			frappe.throw(_("Report {0} is already closed").format(name))
		frappe.db.set_value("Damage Report", name, "status", self.CLOSED)
		frappe.msgprint(_("Damage report {0} closed.").format(name), indicator="green", alert=True)

	# ─────────────────────────────────────────────────────────────────
	# Internal helpers
	# ─────────────────────────────────────────────────────────────────

	def _assert_status(self, doc, expected: str, action: str) -> None:
		if doc.status != expected:
			frappe.throw(
				_("Cannot {0}: report is {1} (expected {2})").format(action, doc.status, expected)
			)

	def _assert_fleet_manager(self) -> None:
		if not frappe.user.has_role("Fleet Manager"):
			frappe.throw(_("Only Fleet Managers can close damage reports"), frappe.PermissionError)
