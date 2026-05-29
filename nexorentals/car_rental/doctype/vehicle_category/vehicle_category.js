frappe.ui.form.on("Vehicle Category", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("View Vehicles"), () => {
				frappe.set_route("List", "Vehicle", { vehicle_category: frm.doc.name });
			});
		}
	},
});
