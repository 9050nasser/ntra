frappe.ui.form.on("Goal", {
	refresh(frm) {
        let result = (frm.doc.custom_weight_progress * frm.doc.custom_weight) /100
        frm.set_value("custom_weight_progress_result", result)
        frm.save();
	},
    custom_weight_progress(frm) {
        update(frm)
        frm.save();
    },
    validate (frm) {
        update(frm)
    }
});

function update(frm) {
    let result = (frm.doc.custom_weight_progress * frm.doc.custom_weight) /100
    frm.set_value("custom_weight_progress_result", result)
}

