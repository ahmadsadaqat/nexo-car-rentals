frappe.ui.form.on("Vehicle Insurance", {
	setup(frm) {
		frm.set_query("vehicle", () => ({
			filters: { registration_stage: "Active" },
		}));
	},

	refresh(frm) {
		_set_status_indicator(frm);
		_add_action_buttons(frm);

		if (!frm.is_new()) {
			frm.add_custom_button(__("All Policies for Vehicle"), () => {
				frappe.set_route("List", "Vehicle Insurance", { vehicle: frm.doc.vehicle });
			});
		}
	},
});

// ─────────────────────────────────────────────────────────────────────────────
// Action buttons
// ─────────────────────────────────────────────────────────────────────────────

function _add_action_buttons(frm) {
	if (frm.is_new()) return;

	const isManager = frappe.user.has_role("Fleet Manager");

	if (frm.doc.status === "Draft" && isManager) {
		frm.add_custom_button(__("Activate Policy"), () => {
			frappe.confirm(__("Activate this insurance policy?"), () => {
				frm.call("activate").then(() => frm.reload_doc());
			});
		}).addClass("btn-success");
	}

	if (["Draft", "Active"].includes(frm.doc.status) && isManager) {
		frm.add_custom_button(__("Cancel Policy"), () => {
			frappe.confirm(__("Cancel this insurance policy?"), () => {
				frm.call("cancel_policy").then(() => frm.reload_doc());
			});
		}, __("Actions"));
	}
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function _set_status_indicator(frm) {
	const colors = {
		Draft:     "grey",
		Active:    "green",
		Expired:   "red",
		Cancelled: "orange",
	};
	frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "grey");
}
