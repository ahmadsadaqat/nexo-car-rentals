"""Vehicle Contract Service — business logic for contract lifecycle management."""

import frappe
from frappe import _
from typing import Optional

from nexorentals.car_rental.services.base import BaseService, require_permission, log_operation
from nexorentals.car_rental.repositories.vehicle_contract_repository import VehicleContractRepository


class VehicleContractService(BaseService):
	"""
	Handles Vehicle Contract lifecycle operations.

	Responsibilities:
	    - Contract activation and termination
	    - Syncing vehicle status when contract changes
	    - Daily expiry processing (called from scheduler)
	    - Expiring contract alerts
	"""

	def __init__(self, user: Optional[str] = None) -> None:
		super().__init__(user)
		self.repo = VehicleContractRepository()

	@require_permission("Vehicle Contract", "write")
	@log_operation("activate_contract")
	def activate(self, contract_name: str) -> None:
		"""Activate a Draft contract and link it to the vehicle."""
		doc = self.repo.get_or_throw(contract_name, for_update=True)
		if doc.status != "Draft":
			frappe.throw(_("Only Draft contracts can be activated"))
		doc.status = "Active"
		doc.save()

	@require_permission("Vehicle Contract", "write")
	@log_operation("terminate_contract")
	def terminate(self, contract_name: str) -> None:
		"""Terminate an Active or Draft contract."""
		doc = self.repo.get_or_throw(contract_name, for_update=True)
		if doc.status not in ("Draft", "Active"):
			frappe.throw(_("Only Draft or Active contracts can be terminated"))
		doc.status = "Terminated"
		doc.save()

	def run_expiry_check(self) -> int:
		"""
		Expire overdue contracts and update vehicle statuses.

		Called by the daily scheduler task in tasks.py.
		Returns count of contracts expired.
		"""
		count = self.repo.expire_overdue()
		if count:
			frappe.logger("nexorentals").info(f"Contract expiry: {count} contract(s) expired")
		return count

	@require_permission("Vehicle Contract", "read")
	def get_expiring_soon(self, days: int = 30) -> list[dict]:
		"""Return contracts expiring within the given number of days."""
		return self.repo.get_expiring_contracts(days)
