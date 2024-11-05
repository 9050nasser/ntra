# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.query_builder.functions import Avg
from frappe.utils import cint, flt
from frappe.utils.nestedset import NestedSet

from hrms.hr.doctype.appraisal_cycle.appraisal_cycle import validate_active_appraisal_cycle
from hrms.hr.utils import validate_active_employee
from pypika import CustomFunction


class Objective(Document):
	pass

@frappe.whitelist()
def get_children(doctype: str, parent: str, is_root: bool = False, **filters) -> list[dict]:
	Goal = frappe.qb.DocType(doctype)

	query = (
		frappe.qb.from_(Goal)
		.select(
			Goal.name.as_("value"),
			Goal.objective.as_("title"),
			Goal.is_group.as_("expandable"),
			Goal.status,
			Goal.employee,
			Goal.employee_name,
			Goal.objective_cycle,
			Goal.progress,
			Goal.kra,
		)
		.where(Goal.status != "Archived")
	)

	if filters.get("employee"):
		query = query.where(Goal.employee == filters.get("employee"))

	if filters.get("appraisal_cycle"):
		query = query.where(Goal.appraisal_cycle == filters.get("appraisal_cycle"))

	if filters.get("goal"):
		query = query.where(Goal.parent_objective == filters.get("goal"))
	elif parent and not is_root:
		# via expand child
		query = query.where(Goal.parent_objective == parent)
	else:
		ifnull = CustomFunction("IFNULL", ["value", "default"])
		query = query.where(ifnull(Goal.parent_objective, "") == "")

	if filters.get("date_range"):
		date_range = frappe.parse_json(filters.get("date_range"))

		query = query.where(
			(Goal.start_date.between(date_range[0], date_range[1]))
			& ((Goal.end_date.isnull()) | (Goal.end_date.between(date_range[0], date_range[1])))
		)

	goals = query.orderby(Goal.employee, Goal.kra).run(as_dict=True)
	_update_goal_completion_status(goals)

	return goals

def _update_goal_completion_status(goals: list[dict]) -> list[dict]:
	for goal in goals:
		if goal.expandable:  # group node
			total_goals = frappe.db.count("Objective", dict(parent_goal=goal.value))

			if total_goals:
				completed = frappe.db.count("Objective", {"parent_objective": goal.value, "status": "Completed"}) or 0
				# set completion status of group node
				goal["completion_count"] = _("{0} of {1} Completed").format(completed, total_goals)

	return goals
