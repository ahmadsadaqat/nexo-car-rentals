from __future__ import annotations

from typing import TYPE_CHECKING

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today

if TYPE_CHECKING:
	from frappe.types import DF

	class VehicleDocument(Document):
		naming_series: DF.Literal["NR-DOC-.YYYY.-.####"]
		vehicle: DF.Link
		vehicle_name: DF.Data | None
		document_type: DF.Literal["Registration", "Mulkiya", "Fitness Certificate", "Road Tax", "Emission Test", "Other"]
		document_number: DF.Data | None
		issue_date: DF.Date | None
		expiry_date: DF.Date
		status: DF.Literal["Valid", "Expired", "Cancelled"]
		issued_by: DF.Data | None
		attachment: DF.Attach | None
		notes: DF.SmallText | None


class VehicleDocument(Document):
	def validate(self) -> None:
		self._validate_dates()
		self._auto_expire()

	def _validate_dates(self) -> None:
		if self.issue_date and self.expiry_date and self.expiry_date < self.issue_date:
			frappe.throw(_("Expiry date cannot be before issue date"))

	def _auto_expire(self) -> None:
		if self.status == "Valid" and self.expiry_date and getdate(self.expiry_date) < getdate(today()):
			self.status = "Expired"

	@frappe.whitelist()
	def cancel_document(self) -> None:
		from nexorentals.car_rental.services.vehicle_document_service import VehicleDocumentService
		VehicleDocumentService().cancel_document(self.name)
		self.reload()
