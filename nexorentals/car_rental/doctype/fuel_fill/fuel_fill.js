frappe.ui.form.on("Fuel Fill", {
	setup(frm) {
		frm.set_query("vehicle", () => ({
			filters: { registration_stage: "Active" },
		}));

		frm.set_query("driver", () => ({
			filters: { status: "Active" },
		}));

		frm.set_query("reservation", () => {
			const filters = { status: ["in", ["Approved", "On Trip"]] };
			if (frm.doc.vehicle) filters.vehicle = frm.doc.vehicle;
			return { filters };
		});
	},

	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Fuel History"), () => {
				frappe.set_route("List", "Fuel Fill", { vehicle: frm.doc.vehicle });
			});
		}
	},

	vehicle(frm) {
		if (frm.doc.vehicle) {
			frappe.db.get_value("Vehicle", frm.doc.vehicle, "current_odometer", (r) => {
				if (r && r.current_odometer) {
					frm.set_value("odometer_at_fill", r.current_odometer);
				}
			});
		}
	},

	liters(frm)         { _calculate_total(frm); },
	cost_per_liter(frm) { _calculate_total(frm); },
});

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function _calculate_total(frm) {
	const liters = frm.doc.liters || 0;
	const costPerLiter = frm.doc.cost_per_liter || 0;
	frm.set_value("total_cost", liters * costPerLiter);
}
