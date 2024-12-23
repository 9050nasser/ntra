import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_employee(source_name, target_doc=None):
	doc = frappe.get_doc("Employee Onboarding", source_name)
	doc.validate_employee_creation()

	def set_missing_values(source, target):
		target.personal_email, target.employee_number, target.designation = frappe.db.get_value("Job Applicant", source.job_applicant, ["email_id", "phone_number", "designation"])
		target.status = "Active"
		target.holiday_list = source.holiday_list
		target.date_of_joining = source.date_of_joining
		target.company , target.scheduled_confirmation_date = frappe.db.get_value("Job Offer", source.job_offer, ["company", "offer_date"])



	doc = get_mapped_doc(
		"Employee Onboarding",
		source_name,
		{
			"Employee Onboarding": {
				"doctype": "Employee",
				"field_map": {
					"first_name": "employee_name",
					"employee_grade": "grade",
				},
			}
		},
		target_doc,
		set_missing_values,
	)
	return doc
