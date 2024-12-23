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
});
