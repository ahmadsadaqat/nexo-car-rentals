frappe.query_reports["Fleet Availability Summary"] = {
	filters: [
		{
			fieldname: "vehicle_category",
			label: __("Category"),
			fieldtype: "Link",
			options: "Vehicle Category",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nAvailable\nReserved\nOn Trip\nUnder Maintenance\nContract Expired\nRetired",
		},
	],
};
