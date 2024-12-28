frappe.ui.form.on("Payroll Entry", {
    refresh(frm) {
        $('[data-fieldname="custom_salary_structure"] input').focus();
    }
});