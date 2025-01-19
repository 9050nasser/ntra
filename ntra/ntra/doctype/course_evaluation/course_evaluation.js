// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Course Evaluation", {
    refresh(frm) {
        frm.fields_dict['table_clme'].grid.get_field('course_evaluation').get_query = function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            var selected_values = frm.fields_dict['table_clme'].grid.get_data().map(function (row) {
                return row.course_evaluation;
            }).filter(function (value) {
                return value; // Filter out undefined/null values
            });

            return {
                filters: [
                    ['Course Evaluation Elements', 'name', 'not in', selected_values]
                ]
            };
        };
        frm.fields_dict['table_zbtv'].grid.get_field('course_evaluation').get_query = function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            var selected_values = frm.fields_dict['table_zbtv'].grid.get_data().map(function (row) {
                return row.course_evaluation;
            }).filter(function (value) {
                return value; // Filter out undefined/null values
            });

            return {
                filters: [
                    ['Course Evaluation Elements', 'name', 'not in', selected_values]
                ]
            };
        };
        frm.fields_dict['table_bapu'].grid.get_field('course_evaluation').get_query = function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            var selected_values = frm.fields_dict['table_bapu'].grid.get_data().map(function (row) {
                return row.course_evaluation;
            }).filter(function (value) {
                return value; // Filter out undefined/null values
            });

            return {
                filters: [
                    ['Course Evaluation Elements', 'name', 'not in', selected_values]
                ]
            };
        };
        frm.fields_dict['table_muzw'].grid.get_field('course_evaluation').get_query = function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            var selected_values = frm.fields_dict['table_muzw'].grid.get_data().map(function (row) {
                return row.course_evaluation;
            }).filter(function (value) {
                return value; // Filter out undefined/null values
            });

            return {
                filters: [
                    ['Course Evaluation Elements', 'name', 'not in', selected_values]
                ]
            };
        };
        frm.fields_dict['table_bgwo'].grid.get_field('course_evaluation').get_query = function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            var selected_values = frm.fields_dict['table_bgwo'].grid.get_data().map(function (row) {
                return row.course_evaluation;
            }).filter(function (value) {
                return value; // Filter out undefined/null values
            });

            return {
                filters: [
                    ['Course Evaluation Elements', 'name', 'not in', selected_values]
                ]
            };
        };
        frm.fields_dict['table_mlfj'].grid.get_field('course_evaluation').get_query = function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            var selected_values = frm.fields_dict['table_mlfj'].grid.get_data().map(function (row) {
                return row.course_evaluation;
            }).filter(function (value) {
                return value; // Filter out undefined/null values
            });

            return {
                filters: [
                    ['Course Evaluation Elements', 'name', 'not in', selected_values]
                ]
            };
        };
        frm.fields_dict['table_ssug'].grid.get_field('course_evaluation').get_query = function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            var selected_values = frm.fields_dict['table_ssug'].grid.get_data().map(function (row) {
                return row.course_evaluation;
            }).filter(function (value) {
                return value; // Filter out undefined/null values
            });

            return {
                filters: [
                    ['Course Evaluation Elements', 'name', 'not in', selected_values]
                ]
            };
        };
    },
    acquired_knowledge_template(frm) {
        get_childtable(frm, frm.doc.acquired_knowledge_template, 'table_clme');
    },
    course_content(frm) {
        get_childtable(frm, frm.doc.course_content, 'table_zbtv');
    },
    instructor_effectiveness_template(frm) {
        get_childtable(frm, frm.doc.instructor_effectiveness_template, 'table_bapu');
    },
    course_material_template(frm) {
        get_childtable(frm, frm.doc.course_material_template, 'table_muzw');
    },
    environment_or_organization_and_venue_template(frm) {
        get_childtable(frm, frm.doc.environment_or_organization_and_venue_template, 'table_bgwo');
    },
    overall_satisfaction_template(frm) {
        get_childtable(frm, frm.doc.overall_satisfaction_template, 'table_mlfj');
    },
    internal_procedures_and_information_template(frm) {
        get_childtable(frm, frm.doc.internal_procedures_and_information_template, 'table_ssug');
    },
});



function get_childtable(frm, fieldname, chidltable) {
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Course Evaluation Elements Template',
            name: fieldname
        },
        callback: function (response) {
            if (response.message) {
                const template = response.message;
                const items = template.elements_table || [];

                // Clear existing child table entries
                frm.clear_table(chidltable);
                // Add each item to the child table
                items.forEach(item => {
                    const row = frm.add_child(chidltable);
                    row.course_evaluation = item.course_evaluation_elements;
                });

                // Refresh the table view
                frm.refresh_field(chidltable);
            }
        }
    });
}
