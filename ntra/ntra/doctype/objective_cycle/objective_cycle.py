# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ObjectiveCycle(Document):
	@frappe.whitelist()
	def set_employees(self):
		"""Pull employees in appraisee list based on selected filters"""
		employees = self.get_employees_for_appraisal()
		appraisal_templates = self.get_appraisal_template_map()

		if employees:
			self.set("table_eujr", [])
			template_missing = False

			for data in employees:
				if not appraisal_templates.get(data.designation):
					template_missing = True

				self.append(
					"table_eujr",
					{
						"employee": data.name,
						"employee_name": data.employee_name,
						"branch": data.branch,
						"designation": data.designation,
						"department": data.department,
						"objective_template": appraisal_templates.get(data.designation),
					},
				)

			if template_missing:
				self.show_missing_template_message()
		else:
			self.set("table_eujr", [])
			frappe.msgprint(_("No employees found for the selected criteria"))

		return self
	
	def get_employees_for_appraisal(self):
		filters = {
			"status": "Active",
			"company": self.company,
		}
		if self.department:
			filters["department"] = self.department
		if self.branch:
			filters["branch"] = self.branch
		if self.designation:
			filters["designation"] = self.designation

		employees = frappe.db.get_all(
			"Employee",
			filters=filters,
			fields=[
				"name",
				"employee_name",
				"branch",
				"designation",
				"department",
			],
		)

		return employees
	
	def get_appraisal_template_map(self):
		designations = frappe.get_all("Designation", fields=["name", "custom_objective_template"])
		appraisal_templates = frappe._dict()

		for entry in designations:
			appraisal_templates[entry.name] = entry.custom_objective_template

		return appraisal_templates

	def show_missing_template_message(self, raise_exception=False):
		msg = _("Objective Template not found for some designations.")
		msg += "<br><br>"
		msg += _(
			"Please set the Objective Template for all the {0} or select the template in the Employees table below."
		).format(f"""<a href='{frappe.utils.get_url_to_list("Designation")}'>Designations</a>""")

		frappe.msgprint(
			msg, title=_("Objective Template Missing"), indicator="yellow", raise_exception=raise_exception
		)