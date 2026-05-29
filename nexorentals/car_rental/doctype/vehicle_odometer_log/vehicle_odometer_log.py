import frappe
from frappe import _
from frappe.model.document import Document
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF


class VehicleOdometerLog(Document):
	if TYPE_CHECKING:
		vehicle: DF.Link
		log_date: DF.Datetime
		odometer_reading: DF.Float
		log_type: DF.Literal["Trip Start", "Trip End", "Manual Update"]
		reservation: DF.Link | None
		previous_reading: DF.Float | None
		km_difference: DF.Float | None
		notes: DF.SmallText | None

	def validate(self) -> None:
		self._validate_reading()
		self._set_km_difference()

	def _validate_reading(self) -> None:
		if self.odometer_reading < 0:
			frappe.throw(_("Odometer reading cannot be negative"))

	def _set_km_difference(self) -> None:
		if self.previous_reading is not None:
			self.km_difference = self.odometer_reading - self.previous_reading
