"""
Vehicle Insurance Service

Manages insurance policy lifecycle:
  Draft → Active → Expired / Cancelled

Includes daily expiry check for scheduler.

Architecture:
    VehicleInsurance controller → VehicleInsuranceService → Repositories → Database
"""

import frappe
from frappe import _
from frappe.utils import getdate, today
from typing import Optional

from nexorentals.car_rental.services.base import BaseService, require_permission, log_operation
from nexorentals.car_rental.repositories.vehicle_insurance_repository import VehicleInsuranceRepository


class VehicleInsuranceService(BaseService):
	"""
	Lifecycle manager for Vehicle Insurance policies.

	Usage:
	    svc = VehicleInsuranceService()
	    svc.activate("NR-INS-2026-0001")
	    svc.run_expiry_check()
	"""

	DRAFT     = "Draft"
	ACTIVE    = "Active"
	EXPIRED   = "Expired"
	CANCELLED = "Cancelled"

	def __init__(self, user: Optional[str] = None) -> None:
		super().__init__(user)
		self.repo = VehicleInsuranceRepository()

	# ─────────────────────────────────────────────────────────────────
	# Transition: Draft → Active
	# ─────────────────────────────────────────────────────────────────

	@require_permission("Vehicle Insurance", "write")
	@log_operation("activate_insurance")
	def activate(self, name: str) -> None:
		"""Activate a Draft insurance policy."""
		doc = self.repo.get_or_throw(name, for_update=True)
		if doc.status != self.DRAFT:
			frappe.throw(_("Cannot activate: policy is {0} (expected Draft)").format(doc.status))
		if getdate(doc.end_date) < getdate(today()):
			frappe.throw(_("Cannot activate an already-expired policy (end date: {0})").format(doc.end_date))
		frappe.db.set_value("Vehicle Insurance", name, "status", self.ACTIVE)
		frappe.msgprint(
			_("Insurance policy {0} is now Active.").format(name), indicator="green", alert=True
		)

	# ─────────────────────────────────────────────────────────────────
	# Transition: Draft / Active → Cancelled
	# ─────────────────────────────────────────────────────────────────

	@require_permission("Vehicle Insurance", "write")
	@log_operation("cancel_insurance")
	def cancel_policy(self, name: str) -> None:
		"""Cancel a Draft or Active insurance policy."""
		doc = self.repo.get_or_throw(name, for_update=True)
		if doc.status in (self.EXPIRED, self.CANCELLED):
			frappe.throw(_("Cannot cancel a {0} policy").format(doc.status))
		frappe.db.set_value("Vehicle Insurance", name, "status", self.CANCELLED)
		frappe.msgprint(_("Insurance policy {0} cancelled.").format(name), indicator="orange", alert=True)

	# ─────────────────────────────────────────────────────────────────
	# Scheduler: daily expiry check
	# ─────────────────────────────────────────────────────────────────

	def run_expiry_check(self) -> None:
		"""Mark Active policies past their end_date as Expired."""
		expired = frappe.get_all(
			"Vehicle Insurance",
			filters=[["status", "=", self.ACTIVE], ["end_date", "<", today()]],
			fields=["name"],
		)
		for row in expired:
			frappe.db.set_value("Vehicle Insurance", row.name, "status", self.EXPIRED)
		if expired:
			frappe.db.commit()
			frappe.logger().info(f"[VehicleInsuranceService] Expired {len(expired)} policies")
