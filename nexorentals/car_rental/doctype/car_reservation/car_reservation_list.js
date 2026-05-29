frappe.listview_settings["Car Reservation"] = {
	get_indicator(doc) {
		const map = {
			"Draft":            [__("Draft"),            "grey",   "status,=,Draft"],
			"Pending Approval": [__("Pending Approval"), "orange", "status,=,Pending Approval"],
			"Approved":         [__("Approved"),         "green",  "status,=,Approved"],
			"On Trip":          [__("On Trip"),          "blue",   "status,=,On Trip"],
			"Completed":        [__("Completed"),        "green",  "status,=,Completed"],
			"Cancelled":        [__("Cancelled"),        "red",    "status,=,Cancelled"],
		};
		return map[doc.status] || [doc.status, "grey"];
	},

	onload(listview) {
		listview.page.add_action_item(__("Show Pending Approvals"), () => {
			listview.filter_area.add([["Car Reservation", "status", "=", "Pending Approval"]]);
		});
		listview.page.add_action_item(__("Show Active Trips"), () => {
			listview.filter_area.add([["Car Reservation", "status", "=", "On Trip"]]);
		});
	},
};
