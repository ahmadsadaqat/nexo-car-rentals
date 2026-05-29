import frappe
from frappe.model.document import Document
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF


class VehicleCategory(Document):
	if TYPE_CHECKING:
		category_name: DF.Data
		description: DF.SmallText | None
