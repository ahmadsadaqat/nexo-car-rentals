frappe.ui.form.on("Damage Report", {
	setup(frm) {
		frm.set_query("vehicle", () => ({
			filters: { registration_stage: "Active" },
		}));

		frm.set_query("reservation", () => {
			const filters = {};
			if (frm.doc.vehicle) filters.vehicle = frm.doc.vehicle;
			return { filters };
		});
	},

	refresh(frm) {
		_set_status_indicator(frm);
		_add_action_buttons(frm);

		if (!frm.is_new()) {
			frm.add_custom_button(__("Damage History"), () => {
				frappe.set_route("List", "Damage Report", { vehicle: frm.doc.vehicle });
			});
		}
	},
});

// ─────────────────────────────────────────────────────────────────────────────
// Action buttons — status-driven
// ─────────────────────────────────────────────────────────────────────────────

function _add_action_buttons(frm) {
	if (frm.is_new()) return;

	const isManager  = frappe.user.has_role("Fleet Manager");
	const isMechanic = frappe.user.has_role("Mechanic") || isManager;
	const isAgent    = frappe.user.has_role("Reservation Agent") || isManager;

	if (frm.doc.status === "Open" && (isMechanic || isAgent)) {
		frm.add_custom_button(__("Start Assessment"), () => {
			frappe.confirm(__("Begin damage assessment?"), () => {
				frm.call("start_assessment").then(() => frm.reload_doc());
			});
		}).addClass("btn-primary");
	}

	if (frm.doc.status === "Under Assessment" && isMechanic) {
		frm.add_custom_button(__("Order Repair"), () => {
			frappe.confirm(
				__("Order repair? Vehicle will be set to Under Maintenance."),
				() => { frm.call("order_repair").then(() => frm.reload_doc()); }
			);
		}).addClass("btn-primary");
	}

	if (frm.doc.status === "Repair Ordered" && isMechanic) {
		frm.add_custom_button(__("Mark Repaired"), () => {
			frappe.confirm(
				__("Mark repair as complete? Vehicle will be set back to Available."),
				() => { frm.call("mark_repaired").then(() => frm.reload_doc()); }
			);
		}).addClass("btn-success");
	}

	if (!["Closed"].includes(frm.doc.status) && isManager) {
		frm.add_custom_button(__("Close Report"), () => {
			frappe.confirm(__("Close this damage report?"), () => {
				frm.call("close_report").then(() => frm.reload_doc());
			});
		}, __("Actions"));
	}
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function _set_status_indicator(frm) {
	const colors = {
		"Open":             "red",
		"Under Assessment": "orange",
		"Repair Ordered":   "blue",
		"Repaired":         "green",
		"Closed":           "grey",
	};
	frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "grey");
}
