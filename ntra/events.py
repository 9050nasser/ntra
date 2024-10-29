import frappe
from frappe import _
from frappe.utils import today


def calculate_rating(doc, method):
    for row in doc.feedback_ratings:
        row.custom_criterial_score_weighted = row.per_weightage * row.custom_criteria_rating_ /100
        row.rating = (row.custom_criterial_score_weighted /100) * 1

def calculate_rating2(doc, method):
    for row in doc.self_ratings:
        row.ccustom_riterial_score_weighted = row.per_weightage * row.custom_criteria_rating_ /100
        row.rating = (row.custom_criterial_score_weighted /100) * 1

def goal_validation(doc, method):
    if doc.end_date < today():
        frappe.throw(_("You Cannot Update Progress After End Date"))