// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Course Costing", {
    validate(frm) {
        estimated_cost(frm)
    }
});

frappe.ui.form.on("Training Elements Table", {
    elements_table_add(frm, cdn, cdt) {
        estimated_cost(frm, cdt, cdn)
	},
    elements_table_remove(frm, cdn, cdt) {
        estimated_cost(frm, cdt, cdn)
	},
});


frappe.ui.form.on("Training Elements Table", "estimated_cost", function(frm, cdt, cdn) {
	estimated_cost(frm, cdt, cdn)
});
frappe.ui.form.on("Training Elements Table", "actual_cost", function(frm, cdt, cdn) {
	estimated_cost(frm, cdt, cdn)
});

function estimated_cost(frm, cdt, cdn) {
    let totalEstimated = frm.doc.elements_table.reduce(function (sum, item) {
        return sum + (item.estimated_cost || 0);
    }, 0);
    let totalActual = frm.doc.elements_table.reduce(function (sum, item) {
        return sum + (item.actual_cost || 0);
    }, 0);
    frm.set_value("total_estimated_cost", totalEstimated)
    frm.set_value("total_actual_cost", totalActual)
    frm.refresh_field("total_estimated_cost")
}

