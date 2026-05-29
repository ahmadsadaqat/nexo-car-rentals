import frappe
from frappe.utils import nowdate
from nexorentals.car_rental.repositories.base import BaseRepository


class RateCardRepository(BaseRepository):
	doctype = "Rate Card"

	def get_active_rate(self, vehicle_category: str) -> dict | None:
		today = nowdate()
		return frappe.db.get_value(
			"Rate Card",
			{
				"vehicle_category": vehicle_category,
				"is_active": 1,
				"effective_from": ["<=", today],
			},
			[
				"name", "daily_rate", "per_km_rate", "minimum_km_per_day",
				"security_deposit", "driver_charges_per_day",
				"extra_km_charge", "late_return_fee_per_hour",
			],
			as_dict=True,
			order_by="effective_from desc",
		)
