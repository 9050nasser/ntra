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
    course_evaluation_elements_template(frm) {
        get_childtable(frm, frm.doc.course_evaluation_elements_template, 'table_cnft');
    }
});

function get_childtable(frm, fieldname, chidltable) {
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Evaluation Element Template',
            name: fieldname
        },
        callback: function (response) {
            if (response.message) {
                const template = response.message;
                const items = template.evaluation_element_table || [];

                // Clear existing child table entries
                frm.clear_table(chidltable);
                // Add each item to the child table
                items.forEach(item => {
                    const row = frm.add_child(chidltable);
                    row.evaluation_elements = item.link_uepu;
                });

                // Refresh the table view
                frm.refresh_field(chidltable);
            }
        }
    });
}
