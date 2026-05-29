import frappe
from frappe import _
from frappe.model.document import Document
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF


class Vehicle(Document):
	if TYPE_CHECKING:
		vehicle_name: DF.Data
		license_plate: DF.Data
		status: DF.Literal["Available", "Reserved", "On Trip", "Under Maintenance", "Contract Expired", "Retired"]
		registration_stage: DF.Literal["Draft", "Registered", "Active", "Suspended", "Retired"]
		vehicle_category: DF.Link | None
		company_make: DF.Data
		model: DF.Data
		model_year: DF.Int | None
		color: DF.Data | None
		image: DF.AttachImage | None
		current_odometer: DF.Float
		last_odometer_update: DF.Datetime | None
		chassis_number: DF.Data | None
		seats: DF.Int | None
		doors: DF.Int | None
		fuel_type: DF.Literal["Petrol", "Diesel", "Electric", "Hybrid", "CNG", "LPG"]
		horsepower: DF.Int | None
		transmission: DF.Literal["Automatic", "Manual"]
		engine_capacity: DF.Data | None
		current_contract: DF.Link | None
		contract_expiry: DF.Date | None
		notes: DF.SmallText | None

	def autoname(self) -> None:
		self.name = self.license_plate

	def validate(self) -> None:
		self._set_vehicle_name()
		self._validate_odometer()

	# ──────────────────────────────────────────────────────────────
	# Private helpers
	# ──────────────────────────────────────────────────────────────

	def _set_vehicle_name(self) -> None:
		if not self.vehicle_name and self.company_make and self.model:
			self.vehicle_name = f"{self.company_make} {self.model} - {self.license_plate}"

	def _validate_odometer(self) -> None:
		if self.current_odometer and self.current_odometer < 0:
			frappe.throw(_("Odometer reading cannot be negative"))
