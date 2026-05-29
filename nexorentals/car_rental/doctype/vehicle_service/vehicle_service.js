frappe.ui.form.on("Vehicle Service", {
	setup(frm) {
		frm.set_query("vehicle", () => ({
			filters: { registration_stage: "Active" },
		}));
	},

	refresh(frm) {
		_set_status_indicator(frm);
		_add_action_buttons(frm);

		if (!frm.is_new()) {
			frm.add_custom_button(__("Service History"), () => {
				frappe.set_route("List", "Vehicle Service", { vehicle: frm.doc.vehicle });
			});
		}
	},

	vehicle(frm) {
		if (frm.doc.vehicle) {
			frappe.db.get_value("Vehicle", frm.doc.vehicle, "current_odometer", (r) => {
				if (r && r.current_odometer) {
					frm.set_value("odometer_at_service", r.current_odometer);
				}
			});
		}
	},
});

// ─────────────────────────────────────────────────────────────────────────────
// Action buttons — role-gated, status-driven
// ─────────────────────────────────────────────────────────────────────────────

function _add_action_buttons(frm) {
	if (frm.is_new()) return;

	const isMechanic = frappe.user.has_role("Mechanic") || frappe.user.has_role("Fleet Manager");

	if (frm.doc.status === "Scheduled" && isMechanic) {
		frm.add_custom_button(__("Start Service"), () => {
			frappe.confirm(
				__("Mark this service as In Progress? Vehicle will be set to Under Maintenance."),
				() => {
					frm.call("start_service").then(() => frm.reload_doc());
				}
			);
		}).addClass("btn-primary");
	}

	if (frm.doc.status === "In Progress" && isMechanic) {
		frm.add_custom_button(__("Complete Service"), () => {
			frappe.confirm(
				__("Mark this service as Completed? Vehicle will be set back to Available."),
				() => {
					frm.call("complete_service").then(() => frm.reload_doc());
				}
			);
		}).addClass("btn-success");
	}
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function _set_status_indicator(frm) {
	const colors = {
		Scheduled:     "orange",
		"In Progress": "blue",
		Completed:     "green",
	};
	frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "grey");
}
