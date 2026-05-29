import frappe
from nexorentals.car_rental.repositories.base import BaseRepository


class VehicleCategoryRepository(BaseRepository):
	doctype = "Vehicle Category"

	def get_all_active(self) -> list[dict]:
		return self.get_list(fields=["name", "category_name", "description"], order_by="category_name asc", limit=100)
