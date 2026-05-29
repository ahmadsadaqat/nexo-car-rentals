from __future__ import annotations

from typing import TYPE_CHECKING

import frappe
from frappe import _
from frappe.model.document import Document

if TYPE_CHECKING:
	from frappe.types import DF

	class FuelFill(Document):
		naming_series: DF.Literal["NR-FUEL-.YYYY.-.####"]
		vehicle: DF.Link
		vehicle_name: DF.Data | None
		fuel_type: DF.Data | None
		fill_date: DF.Date
		reservation: DF.Link | None
		odometer_at_fill: DF.Float | None
		liters: DF.Float
		cost_per_liter: DF.Currency
		total_cost: DF.Currency | None
		station_name: DF.Data | None
		driver: DF.Link | None
		notes: DF.SmallText | None


class FuelFill(Document):
	def validate(self) -> None:
		self._calculate_total_cost()
		self._validate_odometer()

	def _calculate_total_cost(self) -> None:
		liters = self.liters or 0
		cost_per_liter = self.cost_per_liter or 0
		self.total_cost = liters * cost_per_liter

	def _validate_odometer(self) -> None:
		if self.odometer_at_fill and self.odometer_at_fill < 0:
			frappe.throw(_("Odometer at fill cannot be negative"))
