# Copyright (c) 2025, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(filters):
	conditions = []
	conditions_1 = []

    # Adding filters dynamically
	if filters.get("department"):
		conditions.append(f"e.department = '{filters['department']}'")
		conditions_1.append(f"e.department = '{filters['department']}'")
	if filters.get("disclosure_type"):
		conditions.append(f"f.disclosure_type = '{filters['disclosure_type']}'")
	if filters.get("from_date"):
		conditions.append(f"f.received_date >= '{filters['from_date']}'")
	if filters.get("to_date"):
		conditions.append(f"f.received_date <= '{filters['to_date']}'")
	if filters.get("employee"):
		conditions.append(f"e.employee = '{filters['employee']}'")
		conditions_1.append(f"e.employee = '{filters['employee']}'")

	# Combine conditions
	conditions_query = " AND ".join(conditions)
	if conditions_query:
		conditions_query = " AND " + conditions_query
	conditions_query_1 = " AND ".join(conditions_1)
	if conditions_query_1:
		conditions_query_1 = " AND " + conditions_query_1
	query = f"""
		SELECT e.name as name, e.employee_name, e.department,
		(SELECT f.name FROM `tabFinancial Disclosure` f WHERE f.employee = e.name   ORDER BY f.received_date DESC LIMIT 1 ) as financial_disclosure,
		(SELECT f.received_date FROM `tabFinancial Disclosure` f WHERE f.employee = e.name   ORDER BY f.received_date DESC LIMIT 1) as received_date,
		(SELECT f.disclosure_type FROM `tabFinancial Disclosure` f WHERE f.employee = e.name   ORDER BY f.received_date DESC LIMIT 1) as disclosure_type
		FROM `tabEmployee` e
		WHERE e.status = 'Active'
		AND e.name NOT IN (
            SELECT DISTINCT f.employee 
            FROM `tabFinancial Disclosure` f 
            WHERE f.received_date >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)
        )
		{conditions_query_1};
		
	"""
	
	data = frappe.db.sql(query, as_dict=True)
	return data

def get_columns(filters):

	columns = [
        {"label": "Employee ID", "fieldname": "name", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 150},
        {"label": "Financial Disclosure", "fieldname": "financial_disclosure", "fieldtype": "Link", "options": "Financial Disclosure", "width": 200},
        {"label": "Received Date", "fieldname": "received_date", "fieldtype": "Date",  "width": 200},
        {"label": "Disclosure Type", "fieldname": "disclosure_type", "fieldtype": "Data", "width": 150},
    ]
	return columns