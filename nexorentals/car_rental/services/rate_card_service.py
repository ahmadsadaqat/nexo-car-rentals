"""Rate Card Service — business logic for pricing and tariff management."""

import frappe
from frappe import _
from typing import Optional

from nexorentals.car_rental.services.base import BaseService, require_permission
from nexorentals.car_rental.repositories.rate_card_repository import RateCardRepository


class RateCardService(BaseService):
	"""
	Handles pricing and tariff operations.

	Responsibilities:
	    - Active rate lookup by vehicle category
	    - Rental cost calculation
	    - Rate card validation
	"""

	def __init__(self, user: Optional[str] = None) -> None:
		super().__init__(user)
		self.repo = RateCardRepository()

	@require_permission("Rate Card", "read")
	def get_active_rate(self, vehicle_category: str) -> dict | None:
		"""Return active rate card for the given vehicle category."""
		return self.repo.get_active_rate(vehicle_category)

	def calculate_rental_cost(
		self,
		vehicle_category: str,
		days: int,
		total_km: float,
		with_driver: bool = False,
	) -> dict:
		"""
		Calculate total rental cost for a trip.

		Args:
		    vehicle_category: Vehicle category name
		    days: Number of rental days
		    total_km: Total kilometers driven
		    with_driver: Whether driver charges apply

		Returns:
		    dict with base_amount, km_charges, driver_charges, total
		"""
		rate = self.repo.get_active_rate(vehicle_category)
		if not rate:
			frappe.throw(_("No active rate card found for category: {0}").format(vehicle_category))

		base_amount = (rate.daily_rate or 0) * days
		minimum_km = (rate.minimum_km_per_day or 0) * days
		extra_km = max(0, total_km - minimum_km)
		km_charges = extra_km * (rate.per_km_rate or 0)
		driver_charges = (rate.driver_charges_per_day or 0) * days if with_driver else 0

		return {
			"base_amount": base_amount,
			"km_charges": km_charges,
			"driver_charges": driver_charges,
			"total": base_amount + km_charges + driver_charges,
			"security_deposit": rate.security_deposit or 0,
		}
