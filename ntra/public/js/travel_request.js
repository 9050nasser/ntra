frappe.ui.form.on('Travel Request', {
    refresh: function (frm) {
        // Add a custom button
        frm.add_custom_button(__('Create Expense Claim'), function () {
            // Redirect to the Expense Claim form with prefilled values
            frappe.model.open_mapped_doc({
                method: "ntra.event.travel_request.create_expense_claim",
                frm: frm
            });
        }, __('Actions'));
    }
});