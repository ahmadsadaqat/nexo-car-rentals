frappe.ui.form.on("Rate Card", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.is_active) {
			frm.dashboard.set_headline_alert(
				`<span class="text-green">${__("This rate card is currently active")}</span>`
			);
		}
	},

	daily_rate(frm) {
		_update_cost_preview(frm);
	},

	per_km_rate(frm) {
		_update_cost_preview(frm);
	},
});

function _update_cost_preview(frm) {
	if (frm.doc.daily_rate) {
		const weekly = frm.doc.daily_rate * 7;
		const monthly = frm.doc.daily_rate * 30;
		frm.dashboard.set_headline_alert(
			`<span>${__("Estimated: Weekly {0} | Monthly {1}", [
				format_currency(weekly, frm.doc.currency),
				format_currency(monthly, frm.doc.currency),
			])}</span>`
		);
	}
}
