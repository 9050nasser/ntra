// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Provider Evaluation", {
	refresh(frm) {
        frm.fields_dict['table_bnyz'].grid.get_field('provider_evaluation_element').get_query = function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            var selected_values = frm.fields_dict['table_bnyz'].grid.get_data().map(function (row) {
                return row.provider_evaluation_element;
            }).filter(function (value) {
                return value; // Filter out undefined/null values
            });

            return {
                filters: [
                    ['Provider Evaluation Element', 'name', 'not in', selected_values]
                ]
            };
        };
	},
});
