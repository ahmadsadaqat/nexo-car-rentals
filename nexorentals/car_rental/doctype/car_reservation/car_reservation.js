frappe.ui.form.on("Car Reservation", {
	setup(frm) {
		// Only show Available + Active vehicles in vehicle picker
		frm.set_query("vehicle", () => ({
			filters: { status: "Available", registration_stage: "Active" },
		}));

		// Only show Active drivers
		frm.set_query("driver", () => ({
			filters: { status: "Active" },
		}));

		// Filter rate cards to match selected vehicle's category
		frm.set_query("rate_card", () => {
			const filters = { is_active: 1 };
			if (frm.doc.vehicle) {
				frappe.db.get_value("Vehicle", frm.doc.vehicle, "vehicle_category", (r) => {
					if (r && r.vehicle_category) filters.vehicle_category = r.vehicle_category;
				});
			}
			return { filters };
		});
	},

	refresh(frm) {
		_set_status_indicator(frm);
		_add_action_buttons(frm);

		if (!frm.is_new()) {
			frm.add_custom_button(__("Odometer History"), () => {
				frappe.set_route("List", "Vehicle Odometer Log", { vehicle: frm.doc.vehicle });
			});
		}
	},

	trip_start_date(frm) { _update_total_days(frm); },
	trip_end_date(frm)   { _update_total_days(frm); },

	vehicle(frm) {
		if (frm.doc.vehicle) {
			frappe.db.get_value("Vehicle", frm.doc.vehicle, ["current_odometer", "vehicle_category"], (r) => {
				if (!r) return;
				frm.set_value("start_odometer", r.current_odometer || 0);
				// Auto-find matching rate card
				if (r.vehicle_category) {
					frappe.db.get_value(
						"Rate Card",
						{ vehicle_category: r.vehicle_category, is_active: 1 },
						"name",
						(rc) => { if (rc && rc.name) frm.set_value("rate_card", rc.name); }
					);
				}
			});
		}
	},

	rate_card(frm) { _calculate_cost(frm); },
	with_driver(frm) { _calculate_cost(frm); },
	estimated_km(frm) { _calculate_cost(frm); },
	trip_end_date(frm) { _update_total_days(frm); _calculate_cost(frm); },
});

// ─────────────────────────────────────────────────────────────────────────────
// Action buttons — role-gated, status-driven
// ─────────────────────────────────────────────────────────────────────────────

function _add_action_buttons(frm) {
	if (frm.is_new()) return;

	const isAgent    = frappe.user.has_role("Reservation Agent") || frappe.user.has_role("Fleet Manager");
	const isApprover = frappe.user.has_role("Car Rental Approver") || frappe.user.has_role("Fleet Manager");
	const isManager  = frappe.user.has_role("Fleet Manager");

	if (frm.doc.status === "Draft" && isAgent) {
		frm.add_custom_button(__("Submit for Approval"), () => {
			frappe.confirm(__("Submit this reservation for approval?"), () => {
				frm.call("submit_for_approval").then(() => frm.reload_doc());
			});
		}).addClass("btn-primary");
	}

	if (frm.doc.status === "Pending Approval" && isApprover) {
		frm.add_custom_button(__("Approve"), () => {
			frappe.confirm(__("Approve this reservation? The vehicle will be marked Reserved."), () => {
				frm.call("approve").then(() => frm.reload_doc());
			});
		}).addClass("btn-success");

		frm.add_custom_button(__("Reject"), () => {
			frappe.confirm(__("Reject this reservation?"), () => {
				frm.call("reject").then(() => frm.reload_doc());
			});
		}, __("Actions"));
	}

	if (frm.doc.status === "Approved" && isAgent) {
		frm.add_custom_button(__("Start Trip"), () => {
			frappe.confirm(
				__("Start the trip? Start odometer will be recorded from the vehicle."),
				() => {
					frm.call("start_trip").then(() => frm.reload_doc());
				}
			);
		}).addClass("btn-primary");
	}

	if (frm.doc.status === "On Trip" && isAgent) {
		frm.add_custom_button(__("Complete Trip"), () => {
			_show_complete_trip_dialog(frm);
		}).addClass("btn-success");
	}

	if (!["Completed", "Cancelled"].includes(frm.doc.status) && isManager) {
		frm.add_custom_button(__("Cancel Reservation"), () => {
			frappe.confirm(__("Cancel this reservation?"), () => {
				frm.call("cancel_reservation").then(() => frm.reload_doc());
			});
		}, __("Actions"));
	}
}

function _show_complete_trip_dialog(frm) {
	const startOdo = frm.doc.start_odometer || 0;
	const dialog = new frappe.ui.Dialog({
		title: __("Complete Trip"),
		fields: [
			{
				fieldname: "end_odometer",
				fieldtype: "Float",
				label: __("End Odometer (km)"),
				reqd: 1,
				description: __("Vehicle start odometer was {0} km", [startOdo]),
			},
			{ fieldname: "cb", fieldtype: "Column Break" },
			{
				fieldname: "actual_km",
				fieldtype: "Float",
				label: __("Actual KM Driven"),
				description: __("Leave blank to auto-calculate from odometer"),
			},
		],
		primary_action_label: __("Complete Trip"),
		primary_action(values) {
			if (values.end_odometer < startOdo) {
				frappe.msgprint(__("End odometer cannot be less than start odometer ({0} km)", [startOdo]));
				return;
			}
			frappe.call({
				method: "nexorentals.car_rental.api.car_reservation.complete_trip",
				args: {
					name: frm.doc.name,
					end_odometer: values.end_odometer,
					actual_km: values.actual_km || null,
				},
				freeze: true,
				freeze_message: __("Completing trip..."),
				callback(r) {
					if (!r.exc) {
						dialog.hide();
						frm.reload_doc();
						frappe.show_alert({ message: __("Trip completed successfully!"), indicator: "green" });
					}
				},
			});
		},
	});
	dialog.show();
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function _set_status_indicator(frm) {
	const colors = {
		Draft:            "grey",
		"Pending Approval": "orange",
		Approved:         "green",
		"On Trip":        "blue",
		Completed:        "green",
		Cancelled:        "red",
	};
	frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "grey");
}

function _update_total_days(frm) {
	if (frm.doc.trip_start_date && frm.doc.trip_end_date) {
		const diff = frappe.datetime.get_diff(frm.doc.trip_end_date, frm.doc.trip_start_date);
		frm.set_value("total_days", Math.max(1, diff));
	}
}

function _calculate_cost(frm) {
	if (!frm.doc.rate_card || !frm.doc.total_days) return;
	frappe.call({
		method: "nexorentals.car_rental.api.car_reservation.calculate_cost",
		args: {
			rate_card: frm.doc.rate_card,
			total_days: frm.doc.total_days,
			estimated_km: frm.doc.estimated_km || 0,
			with_driver: frm.doc.with_driver ? 1 : 0,
		},
		callback(r) {
			if (r.message) {
				frm.set_value("base_amount",     r.message.base_amount);
				frm.set_value("km_charges",      r.message.km_charges);
				frm.set_value("driver_charges",  r.message.driver_charges);
				frm.set_value("security_deposit", r.message.security_deposit);
				frm.set_value("total_amount",    r.message.total);
			}
		},
	});
}
