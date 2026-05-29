import frappe
from frappe.utils import nowdate
from nexorentals.car_rental.repositories.base import BaseRepository


class VehicleContractRepository(BaseRepository):
	doctype = "Vehicle Contract"

	def get_active_for_vehicle(self, vehicle: str) -> dict | None:
		return frappe.db.get_value(
			"Vehicle Contract",
			{"vehicle": vehicle, "status": "Active"},
			["name", "contract_start_date", "contract_end_date", "owner_name", "status"],
			as_dict=True,
		)

	def get_expiring_contracts(self, days: int = 30) -> list[dict]:
		from frappe.utils import add_days
		threshold = add_days(nowdate(), days)
		return frappe.get_all(
			"Vehicle Contract",
			filters={
				"status": "Active",
				"contract_end_date": ["<=", threshold],
			},
			fields=["name", "vehicle", "owner_name", "contract_end_date"],
		)

	def expire_overdue(self) -> int:
		"""Expire all Active contracts whose end date has passed. Returns count updated."""
		today = nowdate()
		overdue = frappe.get_all(
			"Vehicle Contract",
			filters={"status": "Active", "contract_end_date": ["<", today]},
			fields=["name", "vehicle"],
		)
		for row in overdue:
			frappe.db.set_value("Vehicle Contract", row.name, "status", "Expired")
			if row.vehicle:
				current = frappe.db.get_value("Vehicle", row.vehicle, "current_contract")
				if current == row.name:
					frappe.db.set_value(
						"Vehicle",
						row.vehicle,
						{"status": "Contract Expired", "current_contract": None, "contract_expiry": None},
					)
		return len(overdue)
