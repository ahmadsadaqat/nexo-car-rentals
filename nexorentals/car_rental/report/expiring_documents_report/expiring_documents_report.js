frappe.query_reports["Expiring Documents Report"] = {
	filters: [
		{
			fieldname: "days_ahead",
			label: __("Expiring Within (days)"),
			fieldtype: "Int",
			default: 60,
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "days_left" && data) {
			const days = data.days_left;
			if (days < 0) {
				value = `<span class="text-danger fw-bold">${value}</span>`;
			} else if (days <= 14) {
				value = `<span class="text-warning fw-bold">${value}</span>`;
			}
		}
		return value;
	},
};
