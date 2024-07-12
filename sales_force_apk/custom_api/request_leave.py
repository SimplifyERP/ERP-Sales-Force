import frappe
from frappe.utils import now,getdate,today,format_date,date_diff
from datetime import datetime,timedelta

from hrms.hr.doctype.leave_application.leave_application import get_leaves_for_period,get_leave_balance_on

@frappe.whitelist()
def create_leave_application(user_id, from_date, to_date, half_day, leave_type, reason):
    status = ""
    message = ""
    get_emp_id = frappe.db.get_value('Employee', {'user_id': user_id, 'status': 'Active'}, ['name', 'leave_approver'])
    if get_emp_id[0]:

        from_date_format_change = datetime.strptime(from_date,"%d-%m-%Y").date()
        to_date_format_change = datetime.strptime(to_date,"%d-%m-%Y").date()

        validate_leave_allocation = get_leave_allocation_record(from_date_format_change,user_id,leave_type)
        if validate_leave_allocation:
            leave_balance = get_leave_balance_on(get_emp_id[0],leave_type,from_date_format_change,to_date_format_change,consider_all_leaves_in_the_allocation_period=True,for_consumption=True)
            leave_applied_count = (date_diff(to_date_format_change,from_date_format_change) + 1)
            if float(leave_balance.leave_balance) >= float(leave_applied_count):
                new_leave = frappe.get_doc({
                    'doctype': 'Leave Application',
                    'employee': get_emp_id[0],
                    'from_date': from_date_format_change,
                    'to_date': to_date_format_change,
                    'half_day': half_day,
                    'leave_type': leave_type,
                    'description': reason,
                    'follow_via_email': 0,
                })
                new_leave.insert(ignore_permissions=True)
                frappe.db.commit()
                frappe.db.set_value("Leave Application",new_leave.name,"owner",user_id)
                status = True
                message = "Leave Applied"
            else:
                status = False
                message = "Employee Leave Balance is greater than Applied Leave"
        else:
            status = False
            message = "Employee Have No Leave Allocation"	
    else:
        status = False
        message = "This Employee have no ID "		
    return {"status": status,"message":message}
  
    
def get_leave_allocation_record(date,user_id,leave_type):
    get_emp = frappe.db.get_value('Employee', {'user_id': user_id, 'status': 'Active'}, ['name'])
    if get_emp:
        LeaveAllocation = frappe.qb.DocType("Leave Allocation")
        allocation = (
            frappe.qb.from_(LeaveAllocation)
            .select(LeaveAllocation.name, LeaveAllocation.from_date, LeaveAllocation.to_date)
            .where(
                (LeaveAllocation.employee == get_emp)
                & (LeaveAllocation.leave_type == leave_type)
                & (LeaveAllocation.docstatus == 1)
                & ((date >= LeaveAllocation.from_date) & (date <= LeaveAllocation.to_date))
            )
        ).run(as_dict=True)

    return allocation and allocation[0]




@frappe.whitelist()
def leave_application_list_view(user_id):
    try:
       
        get_emp = frappe.get_all('Employee', filters={'user_id': user_id, 'status': 'Active'}, fields=['*'])

        if get_emp:
            leave_application_list = frappe.get_all('Leave Application',filters={'employee': get_emp[0].name},fields=["*"])

            formatted_leave_list = []

            for leave in leave_application_list:
                leave_data = {
                    'id': leave.name,
                    'name': leave.name,
                    'employee':leave.employee_name,
                    'applied_on': leave.posting_date,
                    'leave_type': leave.leave_type,
                    'leave_duration': leave.total_leave_days,
                    'from_date': leave.from_date,
                    'to_date': leave.to_date,
                    'leave_balance': leave.leave_balance,
                    'reason': leave.description,
                    'half_day': leave.half_day,
                    'status':leave.status
                }

                formatted_leave_list.append(leave_data)

            return {"status": True, "leave_list": formatted_leave_list}
        else:
            return {"status": False}
    except:
       
        return {"status": False}
