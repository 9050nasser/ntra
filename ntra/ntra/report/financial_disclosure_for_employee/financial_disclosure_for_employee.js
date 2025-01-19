// Copyright (c) 2025, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.query_reports["Financial Disclosure For Employee"] = {
	"filters": [
		{
            fieldname: "employee",
            label: __("Employee"),
            fieldtype: "Link",
            options: "Employee",
            default: "",
            ignore_cache: true
        },
		{
            fieldname: "department",
            label: __("Department"),
            fieldtype: "Link",
            options: "Department",
            default: "",
            ignore_cache: true
        },
        {
            fieldname: "disclosure_type",
            label: __("Disclosure Type"),
            fieldtype: "Data",
            default: ""
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: "",
            ignore_cache: true
        },
		{
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: "",
            ignore_cache: true
        }
	]
};
