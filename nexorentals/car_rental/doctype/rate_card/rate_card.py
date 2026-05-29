import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF


class RateCard(Document):
	if TYPE_CHECKING:
		rate_card_name: DF.Data
		vehicle_category: DF.Link | None
		is_active: DF.Check
		currency: DF.Link | None
		daily_rate: DF.Currency
		per_km_rate: DF.Currency | None
		minimum_km_per_day: DF.Float | None
		security_deposit: DF.Currency | None
		driver_charges_per_day: DF.Currency | None
		extra_km_charge: DF.Currency | None
		late_return_fee_per_hour: DF.Currency | None
		fuel_surcharge: DF.Currency | None
		effective_from: DF.Date | None
		effective_to: DF.Date | None
		notes: DF.SmallText | None

	def validate(self) -> None:
		self._validate_dates()
		self._validate_rates()

	def _validate_dates(self) -> None:
		if self.effective_from and self.effective_to:
			if getdate(self.effective_to) < getdate(self.effective_from):
				frappe.throw(_("Effective To date must be after Effective From date"))

	def _validate_rates(self) -> None:
		if self.daily_rate and self.daily_rate <= 0:
			frappe.throw(_("Daily Rate must be greater than zero"))
