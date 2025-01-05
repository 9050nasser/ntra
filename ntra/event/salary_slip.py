import frappe

def get_all_stamp_tax_applicable_components():
    return frappe.get_all(
        "Salary Component",
        filters={"custom_stamp_tax_applicable": 1},
        fields=["name"],
        pluck="name"
    )
    
def get_stamp_tax_amount(doc, method):
    stamp_tax_applicable_components = get_all_stamp_tax_applicable_components()
    print(stamp_tax_applicable_components)
    stamp_tax_amount = 0
    for component in doc.earnings:
        if component.salary_component in stamp_tax_applicable_components:
            stamp_tax_amount += component.amount
    print(f"stamp tax amount: {stamp_tax_amount}")
    return float(stamp_tax_amount)

def stamp_tax_formula(doc, method):
    stamp_tax_amount = get_stamp_tax_amount(doc, method)
    stamp_tax_levels = frappe.get_doc("Stamp Tax", "الدمغة النسبية 2024")
    tax_amount = stamp_tax_amount - stamp_tax_levels.standard_tax_exemption_amount

    for row in stamp_tax_levels.taxable_salary:
        # Check if the tax amount falls within the current row's range
        if tax_amount >= row.from_amount and tax_amount <= row.to_amount:
            # Ensure "الدمغة" is not already in doc.earnings
            if not any(sl.salary_component == "الدمغة" for sl in doc.deductions):
                doc.append("deductions", {
                    "salary_component": "الدمغة",
                    "amount": row.percent_deduction * tax_amount,
                    "additional_amount": 0,
                })

        
    
    
        