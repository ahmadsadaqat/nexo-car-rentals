import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, nowdate
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF


class Driver(Document):
	if TYPE_CHECKING:
		driver_name: DF.Data
		status: DF.Literal["Active", "Inactive", "Suspended"]
		license_number: DF.Data
		license_expiry: DF.Date | None
		id_number: DF.Data | None
		date_of_birth: DF.Date | None
		photo: DF.AttachImage | None
		contact_number: DF.Data | None
		email_id: DF.Data | None
		address: DF.SmallText | None
		linked_user: DF.Link | None
		notes: DF.SmallText | None

	def validate(self) -> None:
		self._check_license_expiry()

	def _check_license_expiry(self) -> None:
		if not self.license_expiry:
			return
		days = date_diff(self.license_expiry, nowdate())
		if days < 0:
			frappe.msgprint(
				_("Driver {0}'s license expired on {1}").format(self.driver_name, self.license_expiry),
				alert=True,
				indicator="red",
			)
		elif days <= 30:
			frappe.msgprint(
				_("Driver {0}'s license expires in {1} day(s) on {2}").format(
					self.driver_name, days, self.license_expiry
				),
				alert=True,
				indicator="orange",
			)
