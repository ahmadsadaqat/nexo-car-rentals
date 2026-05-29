import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, date_diff
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF


class CarReservation(Document):
	if TYPE_CHECKING:
		naming_series: DF.Literal["NR-RES-.YYYY.-.####"]
		status: DF.Literal["Draft", "Pending Approval", "Approved", "On Trip", "Completed", "Cancelled"]
		booking_date: DF.Date
		customer: DF.Link
		customer_name: DF.Data | None
		vehicle: DF.Link
		vehicle_name: DF.Data | None
		driver: DF.Link | None
		driver_name: DF.Data | None
		trip_start_date: DF.Date
		trip_end_date: DF.Date
		total_days: DF.Int | None
		pickup_location: DF.Data
		dropoff_location: DF.Data
		estimated_km: DF.Float | None
		start_odometer: DF.Float | None
		end_odometer: DF.Float | None
		trip_km: DF.Float | None
		rate_card: DF.Link | None
		with_driver: DF.Check
		currency: DF.Link | None
		base_amount: DF.Currency | None
		km_charges: DF.Currency | None
		driver_charges: DF.Currency | None
		security_deposit: DF.Currency | None
		total_amount: DF.Currency | None
		notes: DF.SmallText | None

	def before_validate(self) -> None:
		self._calculate_total_days()

	def validate(self) -> None:
		self._validate_dates()
		self._validate_vehicle_availability()
		self._calculate_cost()

	# ──────────────────────────────────────────────────────────────
	# Private helpers
	# ──────────────────────────────────────────────────────────────

	def _calculate_total_days(self) -> None:
		if self.trip_start_date and self.trip_end_date:
			delta = date_diff(self.trip_end_date, self.trip_start_date)
			self.total_days = max(1, delta)

	def _validate_dates(self) -> None:
		if self.trip_start_date and self.trip_end_date:
			if getdate(self.trip_end_date) < getdate(self.trip_start_date):
				frappe.throw(_("Trip End Date cannot be before Trip Start Date"))

	def _validate_vehicle_availability(self) -> None:
		if self.status not in ("Draft",) or not self.vehicle:
			return
		blocked = ("Reserved", "On Trip", "Under Maintenance", "Contract Expired", "Retired")
		vehicle_status = frappe.db.get_value("Vehicle", self.vehicle, "status")
		if vehicle_status in blocked:
			frappe.throw(
				_("Vehicle {0} is not available for booking (current status: {1})").format(
					self.vehicle, vehicle_status
				)
			)

	def _calculate_cost(self) -> None:
		if not self.rate_card or not self.total_days:
			return
		from nexorentals.car_rental.services.rate_card_service import RateCardService
		rate = frappe.db.get_value(
			"Rate Card",
			self.rate_card,
			["daily_rate", "per_km_rate", "minimum_km_per_day", "security_deposit", "driver_charges_per_day"],
			as_dict=True,
		)
		if not rate:
			return
		base = (rate.daily_rate or 0) * self.total_days
		minimum_km = (rate.minimum_km_per_day or 0) * self.total_days
		actual_km = self.trip_km or self.estimated_km or 0
		extra_km = max(0, actual_km - minimum_km)
		km_ch = extra_km * (rate.per_km_rate or 0)
		drv_ch = (rate.driver_charges_per_day or 0) * self.total_days if self.with_driver else 0
		self.base_amount = base
		self.km_charges = km_ch
		self.driver_charges = drv_ch
		self.security_deposit = rate.security_deposit or 0
		self.total_amount = base + km_ch + drv_ch

	# ──────────────────────────────────────────────────────────────
	# Whitelisted transition methods (called from JS via frm.call)
	# ──────────────────────────────────────────────────────────────

	@frappe.whitelist()
	def submit_for_approval(self) -> None:
		from nexorentals.car_rental.services.car_reservation_service import CarReservationService
		CarReservationService().submit_for_approval(self.name)
		self.reload()

	@frappe.whitelist()
	def approve(self) -> None:
		from nexorentals.car_rental.services.car_reservation_service import CarReservationService
		CarReservationService().approve(self.name)
		self.reload()

	@frappe.whitelist()
	def reject(self) -> None:
		from nexorentals.car_rental.services.car_reservation_service import CarReservationService
		CarReservationService().reject(self.name)
		self.reload()

	@frappe.whitelist()
	def start_trip(self) -> None:
		from nexorentals.car_rental.services.car_reservation_service import CarReservationService
		CarReservationService().start_trip(self.name)
		self.reload()

	@frappe.whitelist()
	def cancel_reservation(self) -> None:
		from nexorentals.car_rental.services.car_reservation_service import CarReservationService
		CarReservationService().cancel_reservation(self.name)
		self.reload()
