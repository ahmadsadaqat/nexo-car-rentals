frappe.ui.form.on("Vehicle Odometer Log", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.km_difference > 0) {
			frm.dashboard.set_headline_alert(
				`<span class="text-blue">${__("{0} km added since last reading", [frm.doc.km_difference])}</span>`
			);
		}
	},

	vehicle(frm) {
		if (frm.doc.vehicle) {
			frappe.db.get_value("Vehicle", frm.doc.vehicle, "current_odometer", (r) => {
				if (r && r.current_odometer) {
					frm.set_value("previous_reading", r.current_odometer);
				}
			});
		}
	},
});
