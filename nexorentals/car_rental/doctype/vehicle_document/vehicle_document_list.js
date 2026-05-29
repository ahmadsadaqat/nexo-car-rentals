frappe.listview_settings["Vehicle Document"] = {
	get_indicator(doc) {
		const map = {
			"Valid":     [__("Valid"),     "green",  "status,=,Valid"],
			"Expired":   [__("Expired"),   "red",    "status,=,Expired"],
			"Cancelled": [__("Cancelled"), "orange", "status,=,Cancelled"],
		};
		return map[doc.status] || [doc.status, "grey"];
	},

	onload(listview) {
		listview.page.add_action_item(__("Show Expiring in 30 Days"), () => {
			const soon = frappe.datetime.add_days(frappe.datetime.get_today(), 30);
			listview.filter_area.add([
				["Vehicle Document", "status", "=", "Valid"],
				["Vehicle Document", "expiry_date", "<=", soon],
			]);
		});
		listview.page.add_action_item(__("Show Expired"), () => {
			listview.filter_area.add([["Vehicle Document", "status", "=", "Expired"]]);
		});
	},
};
