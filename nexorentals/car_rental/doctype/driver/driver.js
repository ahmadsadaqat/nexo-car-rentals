frappe.ui.form.on("Driver", {
	refresh(frm) {
		// License expiry indicator in list view
		if (frm.doc.license_expiry) {
			const today = frappe.datetime.get_today();
			const daysLeft = frappe.datetime.get_diff(frm.doc.license_expiry, today);
			if (daysLeft < 0) {
				frm.dashboard.set_headline_alert(
					`<span class="text-red">${__("License Expired on {0}", [frm.doc.license_expiry])}</span>`
				);
			} else if (daysLeft <= 30) {
				frm.dashboard.set_headline_alert(
					`<span class="text-orange">${__("License expires in {0} days", [daysLeft])}</span>`
				);
			}
		}

		// Status change buttons
		if (frappe.user.has_role("Fleet Manager") && !frm.is_new()) {
			if (frm.doc.status === "Active") {
				frm.add_custom_button(__("Suspend Driver"), () => {
					frappe.confirm(__("Suspend this driver?"), () => {
						frm.set_value("status", "Suspended");
						frm.save();
					});
				}, __("Actions"));
			}
			if (frm.doc.status !== "Active") {
				frm.add_custom_button(__("Set Active"), () => {
					frm.set_value("status", "Active");
					frm.save();
				}, __("Actions"));
			}
		}
	},
});
