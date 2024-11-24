// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Onboarding", {
	refresh(frm) {
        frm.set_query("user", "activities", function (doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            console.log(row.department)
            return {
                filters: {
                    department: row.department
                }
            };
        });
	},
});