"""Base service providing shared utilities for all Car Rental services."""

import frappe
from frappe import _
from typing import Optional
from functools import wraps
from typing import Callable


def require_permission(doctype: str, ptype: str = "read"):
	"""Decorator: checks frappe permission before method executes."""
	def decorator(func: Callable) -> Callable:
		@wraps(func)
		def wrapper(self, *args, **kwargs):
			if not frappe.has_permission(doctype, ptype):
				frappe.throw(
					_("Permission denied: {0} on {1}").format(ptype, doctype),
					frappe.PermissionError,
				)
			return func(self, *args, **kwargs)
		return wrapper
	return decorator


def log_operation(operation: str):
	"""Decorator: logs operation start/end and errors."""
	def decorator(func: Callable) -> Callable:
		@wraps(func)
		def wrapper(self, *args, **kwargs):
			frappe.logger("nexorentals").info(f"[{operation}] start")
			try:
				result = func(self, *args, **kwargs)
				frappe.logger("nexorentals").info(f"[{operation}] done")
				return result
			except Exception as exc:
				frappe.logger("nexorentals").error(f"[{operation}] error: {exc}")
				raise
		return wrapper
	return decorator


class BaseService:
	"""
	Base class for all Car Rental service classes.

	Provides permission checking and shared validation helpers.
	"""

	def __init__(self, user: Optional[str] = None) -> None:
		self.user = user or frappe.session.user

	def check_permission(
		self, doctype: str, ptype: str = "read", doc=None, throw: bool = True
	) -> bool:
		"""Return True if current user has permission; throw or return False otherwise."""
		has = frappe.has_permission(doctype, ptype, doc=doc)
		if not has and throw:
			frappe.throw(
				_("You do not have {0} permission on {1}").format(ptype, doctype),
				frappe.PermissionError,
			)
		return has

	def validate_mandatory(self, data: dict, fields: list[str]) -> None:
		"""Throw if any mandatory field is missing from data."""
		for field in fields:
			if not data.get(field):
				frappe.throw(_("Field {0} is required").format(field))

	def log_activity(self, doctype: str, name: str, action: str, extra: Optional[dict] = None) -> None:
		"""Write a comment/log entry on a document."""
		msg = f"{action}"
		if extra:
			msg += f": {extra}"
		frappe.get_doc(doctype, name).add_comment("Info", msg)
