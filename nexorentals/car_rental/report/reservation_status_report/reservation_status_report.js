frappe.query_reports["Reservation Status Report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nDraft\nPending Approval\nApproved\nOn Trip\nCompleted\nCancelled",
		},
		{
			fieldname: "vehicle_category",
			label: __("Vehicle Category"),
			fieldtype: "Link",
			options: "Vehicle Category",
		},
	],
};
