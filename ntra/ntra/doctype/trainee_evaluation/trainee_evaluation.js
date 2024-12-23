// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Trainee Evaluation", {
    refresh(frm) {
        frm.fields_dict['table_cnft'].grid.get_field('evaluation_elements').get_query = function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            var selected_values = frm.fields_dict['table_cnft'].grid.get_data().map(function (row) {
                return row.evaluation_elements;
            }).filter(function (value) {
                return value; // Filter out undefined/null values
            });

            return {
                filters: [
                    ['Evaluation Elements', 'name', 'not in', selected_values]
                ]
            };
        };

    },
});
