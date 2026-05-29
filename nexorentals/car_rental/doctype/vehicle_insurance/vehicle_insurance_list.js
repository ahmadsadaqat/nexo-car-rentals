frappe.listview_settings["Vehicle Insurance"] = {
	get_indicator(doc) {
		const map = {
			"Draft":     [__("Draft"),     "grey",   "status,=,Draft"],
			"Active":    [__("Active"),    "green",  "status,=,Active"],
			"Expired":   [__("Expired"),   "red",    "status,=,Expired"],
			"Cancelled": [__("Cancelled"), "orange", "status,=,Cancelled"],
		};
		return map[doc.status] || [doc.status, "grey"];
	},

	onload(listview) {
		listview.page.add_action_item(__("Show Active Policies"), () => {
			listview.filter_area.add([["Vehicle Insurance", "status", "=", "Active"]]);
		});
		listview.page.add_action_item(__("Show Expiring Soon"), () => {
			const soon = frappe.datetime.add_days(frappe.datetime.get_today(), 30);
			listview.filter_area.add([
				["Vehicle Insurance", "status", "=", "Active"],
				["Vehicle Insurance", "end_date", "<=", soon],
			]);
		});
	},
};
