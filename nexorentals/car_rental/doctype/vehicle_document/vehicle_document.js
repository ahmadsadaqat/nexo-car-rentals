frappe.ui.form.on("Vehicle Document", {
	setup(frm) {
		frm.set_query("vehicle", () => ({
			filters: { registration_stage: "Active" },
		}));
	},

	refresh(frm) {
		_set_status_indicator(frm);
		_add_action_buttons(frm);
		_show_expiry_warning(frm);

		if (!frm.is_new()) {
			frm.add_custom_button(__("All Documents for Vehicle"), () => {
				frappe.set_route("List", "Vehicle Document", { vehicle: frm.doc.vehicle });
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

	if (frm.doc.status === "Valid" && isManager) {
		frm.add_custom_button(__("Cancel Document"), () => {
			frappe.confirm(__("Mark this document as Cancelled?"), () => {
				frm.call("cancel_document").then(() => frm.reload_doc());
			});
		}, __("Actions"));
	}
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function _set_status_indicator(frm) {
	const colors = {
		Valid:     "green",
		Expired:   "red",
		Cancelled: "orange",
	};
	frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "grey");
}

function _show_expiry_warning(frm) {
	if (!frm.doc.expiry_date || frm.doc.status !== "Valid") return;
	const daysLeft = frappe.datetime.get_diff(frm.doc.expiry_date, frappe.datetime.get_today());
	if (daysLeft <= 30 && daysLeft >= 0) {
		frm.dashboard.add_comment(
			__("This document expires in {0} day(s) on {1}.", [daysLeft, frm.doc.expiry_date]),
			"orange",
			true
		);
	}
}
