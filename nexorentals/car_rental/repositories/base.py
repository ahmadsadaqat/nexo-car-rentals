"""Base repository providing common data access patterns for all Car Rental DocTypes."""

import frappe
from frappe import _
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class BaseRepository(Generic[T]):
	"""
	Generic base repository for Frappe DocType data access.

	Provides standard CRUD, filtering, and counting operations.
	All DocType-specific repositories should extend this class.
	"""

	doctype: str = ""

	def get(self, name: str, for_update: bool = False) -> Optional[T]:
		"""Return document or None if not found."""
		if not frappe.db.exists(self.doctype, name):
			return None
		doc = frappe.get_doc(self.doctype, name)
		if for_update:
			doc.check_permission("write")
		return doc

	def get_or_throw(self, name: str, for_update: bool = False) -> T:
		"""Return document or raise ValidationError if not found."""
		doc = self.get(name, for_update=for_update)
		if doc is None:
			frappe.throw(_("{0} {1} not found").format(self.doctype, name))
		return doc

	def create(self, data: dict) -> T:
		"""Insert a new document and return it."""
		doc = frappe.get_doc({"doctype": self.doctype, **data})
		doc.insert(ignore_permissions=False)
		return doc

	def update(self, name: str, data: dict) -> T:
		"""Update fields on an existing document and return it."""
		doc = self.get_or_throw(name, for_update=True)
		doc.update(data)
		doc.save()
		return doc

	def delete(self, name: str) -> None:
		"""Delete a document."""
		frappe.delete_doc(self.doctype, name)

	def get_list(
		self,
		filters: Optional[dict] = None,
		fields: Optional[list] = None,
		order_by: str = "modified desc",
		limit: int = 20,
		offset: int = 0,
	) -> list[dict]:
		"""Return a list of documents matching filters."""
		return frappe.get_all(
			self.doctype,
			filters=filters or {},
			fields=fields or ["name"],
			order_by=order_by,
			limit=limit,
			start=offset,
		)

	def get_count(self, filters: Optional[dict] = None) -> int:
		"""Return document count matching filters."""
		return frappe.db.count(self.doctype, filters or {})

	def exists(self, filters: dict) -> bool:
		"""Return True if a document matching filters exists."""
		return bool(frappe.db.exists(self.doctype, filters))
