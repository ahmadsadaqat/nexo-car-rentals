"""Scheduled background tasks for Nexorentals."""

import frappe


def check_contract_expiry() -> None:
	"""Daily: expire overdue contracts and update vehicle statuses."""
	from nexorentals.car_rental.services.vehicle_contract_service import VehicleContractService
	VehicleContractService().run_expiry_check()


def check_insurance_expiry() -> None:
	"""Daily: expire insurance policies past their end date."""
	from nexorentals.car_rental.services.vehicle_insurance_service import VehicleInsuranceService
	VehicleInsuranceService().run_expiry_check()


def check_document_expiry() -> None:
	"""Daily: expire vehicle documents past their expiry date."""
	from nexorentals.car_rental.services.vehicle_document_service import VehicleDocumentService
	VehicleDocumentService().run_expiry_check()
