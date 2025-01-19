import frappe
@frappe.whitelist()
def get_leave_details():
    from hrms.hr.doctype.leave_application.leave_application import get_leave_details
    data =  get_leave_details(frappe.form_dict.get("employee"), frappe.form_dict.get("date"))
    leave_types = [{'name':'Leave Without Pay'}, {'name':'Death Leave'}]
    for leave_type in data.get("leave_allocation", {}).keys():
        leave_types.append({"name":leave_type})
    return leave_types
    pass