
import frappe
from frappe.utils import now,getdate,today,format_date
from datetime import datetime
import base64
@frappe.whitelist()
def create_expense_claim(user_id, attach, employee, date, expenses):
	status = ""
	message = ""
	posting_date_format = datetime.strptime(format_date(date), "%m-%d-%Y").date()
	try:
		user_exists = frappe.db.exists("User",{'name':user_id})
		if user_exists:
			decoded_data_inside = base64.b64decode(attach)
			# Get the employee document
			check_employee = frappe.db.exists("Employee",{'user_id':user_exists,"status":"Active"})
			if check_employee:
				get_expense_approver = frappe.db.get_value("Employee",{'status':"Active","name":check_employee},['expense_approver',"company"])
				# Create a new expense claim
				new_expense_claim = frappe.new_doc('Expense Claim')
				new_expense_claim.employee = employee
				new_expense_claim.posting_date = posting_date_format
				# new_expense_claim.payable_account = "Creditors - SAFGPL"
				new_expense_claim.company = get_expense_approver[1]
				# new_expense_claim.expense_approver = get_expense_approver
				for item_data in expenses:
					new_expense_claim.append("expenses", {
						"expense_date":today(),
						"expense_type": item_data.get("expense_type"),
						"default_account":"Travel Expenses - SAFGPL",
						"amount": item_data.get("amount"),
						"description": item_data.get("description"),
					})
				new_expense_claim.save(ignore_permissions=True)
				frappe.db.commit()
				frappe.db.set_value("Expense Claim", new_expense_claim.name, "owner", user_id)
				status = True
				message = "Expense Claim Was Created Successfully"

				#base64 to pdf attach
				file_name_inside = f"{new_expense_claim.name.replace(' ', '_')}_image.pdf"
				new_file_inside = frappe.new_doc('File')
				new_file_inside.file_name = file_name_inside
				new_file_inside.content = decoded_data_inside
				new_file_inside.attached_to_doctype = "Expense Claim"
				new_file_inside.attached_to_name = new_expense_claim.name
				new_file_inside.attached_to_field = "custom_expense_claim_attach"
				new_file_inside.is_private = 0
				new_file_inside.save(ignore_permissions=True)
				frappe.db.commit()
				frappe.db.set_value('Expense Claim', new_expense_claim.name, 'custom_expense_claim_attach', new_file_inside.file_url)
			else:
				status = False
				message = "User ID not Set in Employee MIS Please Contact Admin"    
		else:
			status = False
			message = "User has no ID or User ID Disabled"
		return {"status":status,"message":message}    
	except:
		status = False
		return {"status":status}


# melting claim list view
@frappe.whitelist()
def expense_claim_list(user_id):
	try:
		expense_claim_api = frappe.db.get_all('Expense Claim', {'owner': user_id}, ['*'])

		# Format the response
		formatted_expense_list = []
		for expense_claim in expense_claim_api:
			expense_claim_data = {
				'id': expense_claim.name,
				'name': expense_claim.name,
				'employee': expense_claim.employee,
				'employee_name': expense_claim.employee_name,
				'pdf_attach': expense_claim.custom_expense_claim_attach,
				'posting_date': expense_claim.posting_date,
				'expenses': []
			}

			# Fetch items for each Expense Claim
			expense_claim_details = frappe.get_all('Expense Claim Detail', filters={'parent': expense_claim.name},
												   fields=['expense_type', 'amount','description'])

			for item in expense_claim_details:
				expense_claim_data['expenses'].append({
					'expense_type': item.expense_type,
					'amount': item.amount,
					'description': item.description,
				})

			formatted_expense_list.append(expense_claim_data)

		return {"status": True, "expense_claim": formatted_expense_list}
	except:
		
		return {"status": False}


