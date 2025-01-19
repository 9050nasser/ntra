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

    # Define the limit for the first tax amount slice
    threshold = 10000

    # If the tax amount exceeds 10000, calculate it in two parts
    if tax_amount > threshold:
        # First part: Calculate the deduction for the first 10000 using the first row's percentage
        first_part_amount = threshold
        first_part_deduction = 0  # Assuming no deduction for the first part (adjust if necessary)
        for row in stamp_tax_levels.taxable_salary:
            if first_part_amount >= row.from_amount and first_part_amount <= row.to_amount:
                first_part_deduction = row.percent_deduction * first_part_amount
                break

        # Second part: Calculate the remaining tax amount using the last row's percentage
        remaining_amount = tax_amount - threshold
        remaining_deduction = 0
        for row in stamp_tax_levels.taxable_salary:
            if remaining_amount >= row.from_amount and remaining_amount <= row.to_amount:
                remaining_deduction = row.percent_deduction * remaining_amount
                break

        # Sum both deductions
        total_deduction = first_part_deduction + remaining_deduction

        # Ensure "الدمغة" is not already in doc.deductions
        if not any(sl.salary_component == "الدمغة" for sl in doc.deductions):
            doc.append("deductions", {
                "salary_component": "الدمغة",
                "amount": total_deduction,
                "additional_amount": 0,
            })
    else:
        # If tax amount is less than or equal to 10000, calculate as usual
        for row in stamp_tax_levels.taxable_salary:
            # Check if the tax amount falls within the current row's range
            if tax_amount >= row.from_amount and tax_amount <= row.to_amount:
                # Ensure "الدمغة" is not already in doc.deductions
                if not any(sl.salary_component == "الدمغة" for sl in doc.deductions):
                    doc.append("deductions", {
                        "salary_component": "الدمغة",
                        "amount": row.percent_deduction * tax_amount,
                        "additional_amount": 0,
                    })


def calculate_leave_without_pay(self, method):
    if not self.leave_without_pay:
        return
    base = 0 
    for row in self.earnings:
        if row.salary_component == "Basic":
            base = row.amount
            break
    is_leave_without_pay = False
    for row in self.deductions:
        if row.salary_component == "Leave Without Pay":
            row.amount = (base/30) * self.leave_without_pay
            is_leave_without_pay = True
    if not is_leave_without_pay:
        self.append("deductions", {
            "salary_component": "Leave Without Pay",
            "amount": (base/30) * self.leave_without_pay,
            "additional_amount": 0,
        })
        pass
    pass
    
    
        