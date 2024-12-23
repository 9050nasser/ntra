# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ProviderEvaluation(Document):
	def validate(self):
		self.validate_total_weightage("table_bnyz", "Provider Evaluation")
		self.calculate_score()

	def validate_total_weightage(self, table_name: str, table_label: str) -> None:
			if not self.get(table_name):
				return

			total_weightage = sum(flt(d.item_weight) for d in self.get(table_name))

			if flt(total_weightage, 2) != 100.0:
				frappe.throw(
					_("Total weightage for all {0} must add up to 100. Currently, it is {1}%").format(
						frappe.bold(_(table_label)), total_weightage
					),
					title=_("Incorrect Weightage Allocation"),
				)

	def calculate_score(self):
		if self.table_bnyz:
			for row in self.table_bnyz:
				if row.score:
					row.weighted_score = row.item_weight * row.score /100
					
			total = sum(flt(d.weighted_score) for d in self.get("table_bnyz"))
			self.total_evaluation = total