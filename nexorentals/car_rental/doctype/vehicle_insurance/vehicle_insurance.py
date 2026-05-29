from __future__ import annotations

from typing import TYPE_CHECKING

import frappe
from frappe import _
from frappe.model.document import Document

if TYPE_CHECKING:
	from frappe.types import DF

	class VehicleInsurance(Document):
		naming_series: DF.Literal["NR-INS-.YYYY.-.####"]
		vehicle: DF.Link
		vehicle_name: DF.Data | None
		insurance_company: DF.Data
		policy_number: DF.Data
		insurance_type: DF.Literal["Comprehensive", "Third Party", "Other"]
		start_date: DF.Date
		end_date: DF.Date
		status: DF.Literal["Draft", "Active", "Expired", "Cancelled"]
		premium_amount: DF.Currency | None
		coverage_amount: DF.Currency | None
		notes: DF.SmallText | None


class VehicleInsurance(Document):
	def validate(self) -> None:
		self._validate_dates()

	def _validate_dates(self) -> None:
		if self.start_date and self.end_date and self.end_date < self.start_date:
			frappe.throw(_("End date cannot be before start date"))

	# ─────────────────────────────────────────────────────────────────
	# Whitelisted transitions
	# ─────────────────────────────────────────────────────────────────

	@frappe.whitelist()
	def activate(self) -> None:
		from nexorentals.car_rental.services.vehicle_insurance_service import VehicleInsuranceService
		VehicleInsuranceService().activate(self.name)
		self.reload()

	@frappe.whitelist()
	def cancel_policy(self) -> None:
		from nexorentals.car_rental.services.vehicle_insurance_service import VehicleInsuranceService
		VehicleInsuranceService().cancel_policy(self.name)
		self.reload()
