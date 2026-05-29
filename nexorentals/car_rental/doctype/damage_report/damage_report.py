from __future__ import annotations

from typing import TYPE_CHECKING

import frappe
from frappe import _
from frappe.model.document import Document

if TYPE_CHECKING:
	from frappe.types import DF

	class DamageReport(Document):
		naming_series: DF.Literal["NR-DMG-.YYYY.-.####"]
		vehicle: DF.Link
		vehicle_name: DF.Data | None
		reservation: DF.Link | None
		report_date: DF.Date
		reported_by: DF.Data | None
		damage_type: DF.Literal["Dent", "Scratch", "Glass Damage", "Mechanical", "Flood Damage", "Other"]
		severity: DF.Literal["Minor", "Major", "Total Loss"]
		status: DF.Literal["Open", "Under Assessment", "Repair Ordered", "Repaired", "Closed"]
		description: DF.SmallText
		estimated_repair_cost: DF.Currency | None
		actual_repair_cost: DF.Currency | None
		repair_vendor: DF.Data | None
		notes: DF.SmallText | None


class DamageReport(Document):
	# ─────────────────────────────────────────────────────────────────
	# Whitelisted transitions
	# ─────────────────────────────────────────────────────────────────

	@frappe.whitelist()
	def start_assessment(self) -> None:
		from nexorentals.car_rental.services.damage_report_service import DamageReportService
		DamageReportService().start_assessment(self.name)
		self.reload()

	@frappe.whitelist()
	def order_repair(self) -> None:
		from nexorentals.car_rental.services.damage_report_service import DamageReportService
		DamageReportService().order_repair(self.name)
		self.reload()

	@frappe.whitelist()
	def mark_repaired(self) -> None:
		from nexorentals.car_rental.services.damage_report_service import DamageReportService
		DamageReportService().mark_repaired(self.name)
		self.reload()

	@frappe.whitelist()
	def close_report(self) -> None:
		from nexorentals.car_rental.services.damage_report_service import DamageReportService
		DamageReportService().close_report(self.name)
		self.reload()
