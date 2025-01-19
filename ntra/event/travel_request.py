import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def create_expense_claim(source_name, target_doc=None):

    def update_target_doc(source, target):
        target.employee = source.employee
        target.posting_date = frappe.utils.nowdate()
        target.expenses = []

        # Map expenses from Travel Request
        for expense in source.costings:
            target.append("expenses", {
                "expense_date": expense.custom_expense_date,
                "expense_type": expense.expense_type,
                "amount": expense.total_amount,
                "sanctioned_amount": expense.total_amount,
                "reference_type": "Travel Request",
                "reference_name": source.name
            })

    return get_mapped_doc(
        "Travel Request",
        source_name,
        {
            "Travel Request": {
                "doctype": "Expense Claim",
                "field_map": {
                    "employee": "employee"
                }
            }
        },
        target_doc,
        update_target_doc
    )