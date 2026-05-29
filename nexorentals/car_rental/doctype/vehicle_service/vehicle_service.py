from __future__ import annotations

from typing import TYPE_CHECKING

import frappe
from frappe import _
from frappe.model.document import Document

if TYPE_CHECKING:
	from frappe.types import DF

	class VehicleService(Document):
		naming_series: DF.Literal["NR-SVC-.YYYY.-.####"]
		vehicle: DF.Link
		vehicle_name: DF.Data | None
		service_date: DF.Date
		service_type: DF.Literal["Oil Change", "Tire Rotation", "Brake Service", "AC Service", "General Inspection", "Other"]
		status: DF.Literal["Scheduled", "In Progress", "Completed"]
		odometer_at_service: DF.Float | None
		next_service_km: DF.Float | None
		next_service_date: DF.Date | None
		vendor: DF.Data | None
		service_cost: DF.Currency | None
		description: DF.SmallText | None


class VehicleService(Document):
	def validate(self) -> None:
		self._validate_odometer()

	def _validate_odometer(self) -> None:
		if self.odometer_at_service and self.odometer_at_service < 0:
			frappe.throw(_("Odometer at service cannot be negative"))

	# ─────────────────────────────────────────────────────────────────
	# Whitelisted transitions (called via frm.call from JS)
	# ─────────────────────────────────────────────────────────────────

	@frappe.whitelist()
	def start_service(self) -> None:
		from nexorentals.car_rental.services.vehicle_service_service import VehicleServiceService
		VehicleServiceService().start_service(self.name)
		self.reload()

	@frappe.whitelist()
	def complete_service(self) -> None:
		from nexorentals.car_rental.services.vehicle_service_service import VehicleServiceService
		VehicleServiceService().complete_service(self.name)
		self.reload()
