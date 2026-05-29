"""
Vehicle Document Service

Manages document validity lifecycle and daily expiry checks.

Architecture:
    VehicleDocument controller → VehicleDocumentService → Repositories → Database
"""

import frappe
from frappe import _
from frappe.utils import today
from typing import Optional

from nexorentals.car_rental.services.base import BaseService, require_permission, log_operation
from nexorentals.car_rental.repositories.vehicle_document_repository import VehicleDocumentRepository


class VehicleDocumentService(BaseService):
	"""
	Manages vehicle document validity and expiry.

	Usage:
	    svc = VehicleDocumentService()
	    svc.cancel_document("NR-DOC-2026-0001")
	    svc.run_expiry_check()
	"""

	VALID     = "Valid"
	EXPIRED   = "Expired"
	CANCELLED = "Cancelled"

	def __init__(self, user: Optional[str] = None) -> None:
		super().__init__(user)
		self.repo = VehicleDocumentRepository()

	@require_permission("Vehicle Document", "write")
	@log_operation("cancel_document")
	def cancel_document(self, name: str) -> None:
		"""Cancel a Valid document."""
		doc = self.repo.get_or_throw(name, for_update=True)
		if doc.status in (self.EXPIRED, self.CANCELLED):
			frappe.throw(_("Cannot cancel a {0} document").format(doc.status))
		frappe.db.set_value("Vehicle Document", name, "status", self.CANCELLED)
		frappe.msgprint(_("Document {0} cancelled.").format(name), indicator="orange", alert=True)

	def run_expiry_check(self) -> None:
		"""Mark Valid documents past their expiry_date as Expired."""
		overdue = self.repo.get_overdue()
		for row in overdue:
			frappe.db.set_value("Vehicle Document", row.name, "status", self.EXPIRED)
		if overdue:
			frappe.db.commit()
			frappe.logger().info(f"[VehicleDocumentService] Expired {len(overdue)} documents")
