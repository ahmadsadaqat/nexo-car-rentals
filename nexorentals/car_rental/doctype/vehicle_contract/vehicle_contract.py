import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF


class VehicleContract(Document):
	if TYPE_CHECKING:
		vehicle: DF.Link
		status: DF.Literal["Draft", "Active", "Expired", "Terminated"]
		contract_start_date: DF.Date
		contract_end_date: DF.Date
		owner_type: DF.Literal["Individual", "Company"]
		owner_name: DF.Data | None
		owner_contact: DF.Data | None
		linked_supplier: DF.Link | None
		contract_amount: DF.Currency | None
		currency: DF.Link | None
		payment_frequency: DF.Literal["", "Monthly", "Quarterly", "Yearly", "One-time"]
		security_deposit: DF.Currency | None
		terms_and_conditions: DF.TextEditor | None
		notes: DF.SmallText | None

	def validate(self) -> None:
		self._validate_dates()
		self._auto_set_expired_status()

	def on_update(self) -> None:
		self._sync_vehicle_contract()

	def _validate_dates(self) -> None:
		if self.contract_start_date and self.contract_end_date:
			if getdate(self.contract_end_date) <= getdate(self.contract_start_date):
				frappe.throw(_("Contract End Date must be after Contract Start Date"))

	def _auto_set_expired_status(self) -> None:
		if (
			self.contract_end_date
			and getdate(self.contract_end_date) < getdate(nowdate())
			and self.status != "Terminated"
		):
			self.status = "Expired"

	def _sync_vehicle_contract(self) -> None:
		if not self.vehicle:
			return
		if self.status == "Active":
			frappe.db.set_value(
				"Vehicle",
				self.vehicle,
				{"current_contract": self.name, "contract_expiry": self.contract_end_date},
			)
		elif self.status in ("Expired", "Terminated"):
			current = frappe.db.get_value("Vehicle", self.vehicle, "current_contract")
			if current == self.name:
				frappe.db.set_value(
					"Vehicle",
					self.vehicle,
					{"status": "Contract Expired", "current_contract": None, "contract_expiry": None},
				)

	@frappe.whitelist()
	def activate(self) -> None:
		from nexorentals.car_rental.services.vehicle_contract_service import VehicleContractService
		VehicleContractService().activate(self.name)
		self.reload()

	@frappe.whitelist()
	def terminate(self) -> None:
		from nexorentals.car_rental.services.vehicle_contract_service import VehicleContractService
		VehicleContractService().terminate(self.name)
		self.reload()
