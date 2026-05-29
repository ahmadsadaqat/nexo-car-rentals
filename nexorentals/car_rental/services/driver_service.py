"""Driver Service — business logic for Driver management."""

import frappe
from frappe import _
from typing import Optional

from nexorentals.car_rental.services.base import BaseService, require_permission, log_operation
from nexorentals.car_rental.repositories.driver_repository import DriverRepository


class DriverService(BaseService):
	"""
	Handles business operations for the Driver DocType.

	Responsibilities:
	    - Driver status management
	    - License expiry validation and alerts
	    - Active driver lookup for reservations
	"""

	def __init__(self, user: Optional[str] = None) -> None:
		super().__init__(user)
		self.repo = DriverRepository()

	@require_permission("Driver", "read")
	def get_active_drivers(self) -> list[dict]:
		"""Return all active drivers available for assignment."""
		return self.repo.get_active_drivers()

	@require_permission("Driver", "read")
	def get_expiring_licenses(self, days: int = 30) -> list[dict]:
		"""Return drivers whose licenses expire within the given number of days."""
		return self.repo.get_expiring_licenses(days)

	def validate_driver_for_assignment(self, driver_name: str) -> None:
		"""
		Ensure driver is active and license is valid.

		Raises:
		    frappe.ValidationError: If driver is inactive or license expired.
		"""
		from frappe.utils import getdate, nowdate
		doc = self.repo.get_or_throw(driver_name)
		if doc.status != "Active":
			frappe.throw(_("Driver {0} is not active (status: {1})").format(doc.driver_name, doc.status))
		if doc.license_expiry and getdate(doc.license_expiry) < getdate(nowdate()):
			frappe.throw(_("Driver {0}'s license expired on {1}").format(doc.driver_name, doc.license_expiry))
