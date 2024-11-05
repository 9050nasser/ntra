// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Objective Cycle", {
	refresh(frm) {

	},
    get_employees(frm) {
		frappe.call({
			method: "set_employees",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Fetching Employees"),
			callback: function () {
				refresh_field("table_eujr");
				frm.dirty();
			},
		});
	},
});
