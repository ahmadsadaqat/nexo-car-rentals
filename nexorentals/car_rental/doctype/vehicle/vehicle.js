frappe.ui.form.on("Vehicle", {
	refresh(frm) {
		frm.set_indicator_formatter("status", (row) => {
			const map = {
				"Available": "green",
				"Reserved": "orange",
				"On Trip": "blue",
				"Under Maintenance": "yellow",
				"Contract Expired": "red",
				"Retired": "grey",
			};
			return map[row.status] || "grey";
		});

		// Stage transition buttons for Fleet Managers
		if (frappe.user.has_role("Fleet Manager")) {
			if (frm.doc.registration_stage === "Draft") {
				frm.add_custom_button(__("Mark as Registered"), () => {
					frm.set_value("registration_stage", "Registered");
					frm.save();
				}, __("Actions"));
			}
			if (frm.doc.registration_stage === "Registered") {
				frm.add_custom_button(__("Activate Vehicle"), () => {
					frm.set_value("registration_stage", "Active");
					frm.set_value("status", "Available");
					frm.save();
				}, __("Actions"));
			}
			if (frm.doc.registration_stage === "Active" && frm.doc.status !== "Retired") {
				frm.add_custom_button(__("Send to Maintenance"), () => {
					frm.set_value("status", "Under Maintenance");
					frm.save();
				}, __("Actions"));
				frm.add_custom_button(__("Mark Available"), () => {
					frm.set_value("status", "Available");
					frm.save();
				}, __("Actions"));
			}
		}
	},

	company_make(frm) {
		_auto_set_vehicle_name(frm);
	},

	model(frm) {
		_auto_set_vehicle_name(frm);
	},

	license_plate(frm) {
		_auto_set_vehicle_name(frm);
	},
});

function _auto_set_vehicle_name(frm) {
	if (!frm.doc.vehicle_name && frm.doc.company_make && frm.doc.model && frm.doc.license_plate) {
		frm.set_value("vehicle_name", `${frm.doc.company_make} ${frm.doc.model} - ${frm.doc.license_plate}`);
	}
}
