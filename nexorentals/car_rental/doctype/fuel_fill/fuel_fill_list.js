frappe.listview_settings["Fuel Fill"] = {
	add_fields: ["liters", "total_cost", "fuel_type"],

	get_indicator(doc) {
		return [__(doc.fuel_type || "Fuel"), "blue", "vehicle,=," + doc.vehicle];
	},

	onload(listview) {
		listview.page.add_action_item(__("This Vehicle"), () => {
			// placeholder — filter is set via route
		});
	},
};
