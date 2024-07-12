import frappe
from frappe.utils import now,getdate,today,format_date,nowdate,add_months
from datetime import datetime
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
# from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool.create_payment_entry_bts


@frappe.whitelist()
def create_payment_entry(user_id,db,outlet,posting_date,paid_amount,mode_of_payment,reference_no,date,invoice_id):
    status = ""
    message = ""
    posting_date_format = datetime.strptime(format_date(posting_date), "%m-%d-%Y").date()
    refrence_date = datetime.strptime(format_date(date), "%d-%m-%Y").date()
    try:
        check_user_id = frappe.db.exists('User',{'name':user_id})
        if check_user_id:
            account_paid_to = get_payment_entry_account_paid_to(db)
            get_sales_invoice = frappe.get_doc("Sales Invoice", invoice_id)
            dt = "Sales Invoice"
            dn = get_sales_invoice.name
            payment_entry = get_payment_entry(dt,dn)
            payment_entry.flags.ignore_mandatory = True
            payment_entry.company = db
            payment_entry.posting_date = posting_date_format
            payment_entry.mode_of_payment = mode_of_payment
            payment_entry.payment_type = "Receive" 
            payment_entry.party_type = "Customer"
            payment_entry.party = outlet
            payment_entry.reference_no = reference_no
            payment_entry.reference_date = refrence_date
            payment_entry.paid_to = account_paid_to
            payment_entry.paid_amount = paid_amount
            payment_entry.received_amount = paid_amount
            payment_entry.insert(ignore_permissions=True)
            payment_entry.save()
            frappe.db.set_value("Payment Entry",payment_entry.name,"owner",user_id)
            status = True
            message = "New Payment Entry Created"
        else:
            status = False
        return {"status":status,"message":message}    
    except Exception as e:
        return{"status":False,"message":e}    

def get_payment_entry_account_paid_to(company):
    get_account_paid_to = frappe.db.get_value('Account',{'company':company,'account_type':"Cash"},['name'])
    return get_account_paid_to

#payment entry list
@frappe.whitelist()
def payment_entry_list(user_id):
    try:
        payment_entry_list = frappe.get_all('Payment Entry', {'owner': user_id}, ['*'])
        formatted_payment_list = []
        for payment_entry in payment_entry_list:
            net_balance = payment_entry.difference_amount - payment_entry.total_allocated_amount
            payment_entry_data = {
                'id': payment_entry.name,
                'name': payment_entry.name,
                'select_db': payment_entry.company,
                'select_outlet': payment_entry.party,
                'select_date': payment_entry.posting_date,
                'paid_amount': payment_entry.paid_amount,
                'mode_of_payment': payment_entry.mode_of_payment,
                'date': payment_entry.posting_date,
                'transaction_reference_number': payment_entry.reference_no,
                'total_amount': payment_entry.paid_amount,
                'balance': payment_entry.difference_amount,
                'allocated': payment_entry.total_allocated_amount,
                'net_balance': net_balance,
                'references': []
            }
            references = frappe.get_all('Payment Entry Reference', {'parent': payment_entry.name}, ['*'])
            for item in references:
                payment_entry_data['references'].append({
                    'invoice_no': item.reference_name,
                    'invoice_date': item.due_date,
                    'amount': item.allocated_amount,
                    'balance': item.outstanding_amount
                })
            formatted_payment_list.append(payment_entry_data)

        return {"status": True, "Payment_Entry": formatted_payment_list}
    except:
        return {"status": False}

#sales outlet details
@frappe.whitelist()
def sales_outlet_details(user_id,company,outlet):
    status = ""
    try:
        check_user_id = frappe.db.exists("User",{'name':user_id})
        if check_user_id:
            customer = frappe.db.get_value('Customer',{'name':outlet},['customer_name','territory'])
            freezer_data = frappe.db.get_value('Freezer Data',{'dealer':outlet},['make','model','capacity','basket','serial_no'])
            current_month_sales_amount = outlet_current_month_sales(outlet,user_id,company)
            third_month_sales_amount = outlet_third_month_sales(outlet,user_id,company) or 0
            second_month_sales_amount = outlet_second_month_sales(outlet,user_id,company) or 0
            first_month_sales_amount = outlet_first_month_sales(outlet,user_id,company) or 0
            outlet_details_list = {
                "outlte_name":customer[0],
                "status":"Active",
                "route":customer[1],
                "current_month_sales":current_month_sales_amount,
                "third_month_sales_amount":third_month_sales_amount,
                "second_month_sales_amount":second_month_sales_amount,
                "first_month_sales_amount":first_month_sales_amount,
                "freezer_make_and_model":f"{freezer_data[0]}|{freezer_data[1]}",
                "freezer_capacity":freezer_data[2],
                "no_of_baskets":freezer_data[3],
                "freezer_serial_number":freezer_data[4]
            }
            status = True
        else:
            status = False  
        return {"status":status,"outlet_details_list":outlet_details_list}    
    except:
        status = False
        return{"status":status}  

#current month sales order get the rounded total amount and sum it       
def outlet_current_month_sales(outlet,user_id,company):
    current_month_sales_amount = 0.0
    today = nowdate()
    month_start_date = frappe.utils.data.get_first_day(today)
    month_end_date = frappe.utils.data.get_last_day(today)
    get_sales_amount = frappe.db.sql(""" select sum(rounded_total) as net_total from `tabSales Order` where company = '%s' and customer = '%s' and owner = '%s' and transaction_date between '%s' and '%s' and docstatus = 1 """%(company,outlet,user_id,month_start_date,month_end_date),as_dict=1) or 0
    if get_sales_amount:
        current_month_sales_amount = get_sales_amount[0]['net_total']
    else:
        current_month_sales_amount = 0.0
    return current_month_sales_amount

#third month sales order get the rounded total amount and sum it    
def outlet_third_month_sales(outlet,user_id,company):
    third_month_sales_amount = 0
    current_date = nowdate()

    third_month_start_date = frappe.utils.data.get_first_day(current_date)

    get_third_month_start_date = add_months(third_month_start_date,-1)
    get_third_month_end_date = frappe.utils.data.get_last_day(get_third_month_start_date)
    
    get_sales_amount = frappe.db.sql(""" select sum(rounded_total) as net_total from `tabSales Order` where company = '%s' and customer = '%s' and owner = '%s' and transaction_date between '%s' and '%s' and docstatus = 1 """ % (company, outlet, user_id, get_third_month_start_date, get_third_month_end_date), as_dict=1)
    third_month_sales_amount = get_sales_amount[0]['net_total'] if get_sales_amount and get_sales_amount[0]['net_total'] is not None else 0
    return third_month_sales_amount

#second month sales order get the rounded total amount and sum it 
def outlet_second_month_sales(outlet,user_id,company):
    second_month_sales_amount = 0.0
    current_date = nowdate()

    second_month_start_date = frappe.utils.data.get_first_day(current_date)

    get_second_month_start_date = add_months(second_month_start_date,-2)
    get_second_month_end_date = frappe.utils.data.get_last_day(get_second_month_start_date)
    
    get_sales_amount = frappe.db.sql(""" select sum(rounded_total) as net_total from `tabSales Order` where company = '%s' and customer = '%s' and owner = '%s' and transaction_date between '%s' and '%s' and docstatus = 1 """ % (company, outlet, user_id, get_second_month_start_date, get_second_month_end_date), as_dict=1)
    second_month_sales_amount = get_sales_amount[0]['net_total'] if get_sales_amount and get_sales_amount[0]['net_total'] is not None else 0
    return second_month_sales_amount

#first month sales order get the rounded total amount and sum it 
def outlet_first_month_sales(outlet,user_id,company):
    first_month_sales_amount = 0.0
    current_date = nowdate()

    first_month_start_date = frappe.utils.data.get_first_day(current_date)

    get_first_month_start_date = add_months(first_month_start_date,-3)
    get_first_month_end_date = frappe.utils.data.get_last_day(get_first_month_start_date)
    
    get_sales_amount = frappe.db.sql(""" select sum(rounded_total) as net_total from `tabSales Order` where company = '%s' and customer = '%s' and owner = '%s' and transaction_date between '%s' and '%s' and docstatus = 1 """ % (company, outlet, user_id, get_first_month_start_date, get_first_month_end_date), as_dict=1)
    first_month_sales_amount = get_sales_amount[0]['net_total'] if get_sales_amount and get_sales_amount[0]['net_total'] is not None else 0
    return first_month_sales_amount

@frappe.whitelist()
def get_payment_entry_invoice_data(user_id,company,outlet):
    status = ""
    try:
        check_user_id = frappe.db.exists("User",{'name':user_id})
        if check_user_id:
            get_sales_invoice = frappe.db.get_all("Sales Invoice",{'owner':user_id,'company':company,'customer':outlet},['name','posting_date','rounded_total','outstanding_amount'])
            status = True
        else:
            status = False
        return{"status":status,"type_of_payment_entry":get_sales_invoice}    
    except:
        status = False
        return{"status":status}