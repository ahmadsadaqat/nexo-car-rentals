frappe.listview_settings["Damage Report"] = {
	get_indicator(doc) {
		const map = {
			"Open":             [__("Open"),             "red",    "status,=,Open"],
			"Under Assessment": [__("Under Assessment"), "orange", "status,=,Under Assessment"],
			"Repair Ordered":   [__("Repair Ordered"),   "blue",   "status,=,Repair Ordered"],
			"Repaired":         [__("Repaired"),         "green",  "status,=,Repaired"],
			"Closed":           [__("Closed"),           "grey",   "status,=,Closed"],
		};
		return map[doc.status] || [doc.status, "grey"];
	},

	onload(listview) {
		listview.page.add_action_item(__("Show Open Reports"), () => {
			listview.filter_area.add([["Damage Report", "status", "=", "Open"]]);
		});
		listview.page.add_action_item(__("Show Active (non-closed)"), () => {
			listview.filter_area.add([["Damage Report", "status", "not in", ["Closed"]]]);
		});
	},
};
