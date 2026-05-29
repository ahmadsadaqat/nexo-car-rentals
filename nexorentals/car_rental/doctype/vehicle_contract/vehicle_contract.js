frappe.ui.form.on("Vehicle Contract", {
	refresh(frm) {
		_set_status_color(frm);

		if (!frm.is_new()) {
			if (frm.doc.status === "Draft" && frappe.user.has_role("Fleet Manager")) {
				frm.add_custom_button(__("Activate Contract"), () => {
					frappe.confirm(
						__("Activate this contract and link it to the vehicle?"),
						() => {
							frm.call("activate").then(() => frm.reload_doc());
						}
					);
				}).addClass("btn-primary");
			}

			if (["Draft", "Active"].includes(frm.doc.status) && frappe.user.has_role("Fleet Manager")) {
				frm.add_custom_button(__("Terminate Contract"), () => {
					frappe.confirm(
						__("Are you sure you want to terminate this contract?"),
						() => {
							frm.call("terminate").then(() => frm.reload_doc());
						}
					);
				}, __("Actions"));
			}
		}

		// Days remaining indicator
		if (frm.doc.status === "Active" && frm.doc.contract_end_date) {
			const daysLeft = frappe.datetime.get_diff(frm.doc.contract_end_date, frappe.datetime.get_today());
			if (daysLeft <= 0) {
				frm.dashboard.set_headline_alert(
					`<span class="text-red">${__("Contract has expired")}</span>`
				);
			} else if (daysLeft <= 30) {
				frm.dashboard.set_headline_alert(
					`<span class="text-orange">${__("Contract expires in {0} days", [daysLeft])}</span>`
				);
			} else {
				frm.dashboard.set_headline_alert(
					`<span class="text-green">${__("{0} days remaining", [daysLeft])}</span>`
				);
			}
		}
	},
});

function _set_status_color(frm) {
	const colors = { Draft: "grey", Active: "green", Expired: "red", Terminated: "orange" };
	const color = colors[frm.doc.status] || "grey";
	frm.page.set_indicator(frm.doc.status, color);
}
