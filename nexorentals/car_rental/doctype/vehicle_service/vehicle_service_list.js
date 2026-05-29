frappe.listview_settings["Vehicle Service"] = {
	get_indicator(doc) {
		const map = {
			"Scheduled":    [__("Scheduled"),    "orange", "status,=,Scheduled"],
			"In Progress":  [__("In Progress"),  "blue",   "status,=,In Progress"],
			"Completed":    [__("Completed"),    "green",  "status,=,Completed"],
		};
		return map[doc.status] || [doc.status, "grey"];
	},

	onload(listview) {
		listview.page.add_action_item(__("Show Scheduled"), () => {
			listview.filter_area.add([["Vehicle Service", "status", "=", "Scheduled"]]);
		});
		listview.page.add_action_item(__("Show In Progress"), () => {
			listview.filter_area.add([["Vehicle Service", "status", "=", "In Progress"]]);
		});
	},
};
