import frappe
from frappe.utils import now,getdate,today,get_time,format_date,format_time
from datetime import datetime


@frappe.whitelist()
def activites_data(user_id,date):
    get_user_id = frappe.db.exists('User', {'name': user_id, 'enabled':1})
    if get_user_id:
        #global variables        
        get_in_time = ""
        get_out_time = ""
        current_date = datetime.strptime(format_date(date), "%d-%m-%Y").date()
        get_emp = frappe.db.get_value('Employee',{'user_id':user_id,'status':'Active'},['name'])
        if get_emp:
            # Employee Checkin data
            check_in_time = frappe.db.exists('Employee Checkin',{'employee':get_emp,'custom_punch_date':current_date,'log_type':'IN'})
            if check_in_time:
                emp_checkin_in = frappe.get_doc('Employee Checkin',check_in_time)
                get_in_time = format_time(emp_checkin_in.time)
            else:
                get_in_time = ""  
            check_out_time = frappe.db.exists('Employee Checkin',{'employee':get_emp,'custom_punch_date':current_date,'log_type':'OUT'})
            if check_out_time:
                emp_checkin_out = frappe.get_doc('Employee Checkin',check_out_time)
                get_out_time = format_time(emp_checkin_out.time)
            else:
                get_out_time = ""    
        else:
            get_in_time = ""
        get_new_call = get_lead(user_id,date)
        get_outlet = get_customer(user_id,date)
        get_po = get_purchase_order(user_id,date)
        get_so = get_sales_order(user_id,date)
        get_payment = get_payment_entry(user_id,date)
        get_claim = get_melting_claim(user_id,date)
        
    #overall activites response    
    activites_data_page = {
        "punch_data_time":[
            {
                "punch_in":get_in_time,
                "punch_out":get_out_time
            }
        ],
        "new_call_data":get_new_call,
        "outlet":get_outlet,
        "purchase_order":get_po,
        "sales_order":get_so,
        "payment_entry":get_payment,
        "melting_claim":get_claim 
    }       
    return {"status":True,"activites_page_data":activites_data_page}

#lead activity data
def get_lead(user_id,date):
    lead_data = ""
    current_date = datetime.strptime(format_date(date), "%d-%m-%Y").date()
    try:
        lead = frappe.db.sql("""
            SELECT
                name,
                DATE_FORMAT(creation, '%%d-%%m-%%Y') as formatted_date,
                TIME_FORMAT(STR_TO_DATE(creation, '%%Y-%%m-%%d %%H:%%i:%%s'), '%%H:%%i:%%s') as created_time
            FROM
                `tabLead`
            WHERE
                owner = %s AND
                DATE(creation) = %s
        """, (user_id,current_date), as_dict=True) or ""
        if lead:
            lead_data = lead
        else:
            lead_data = []   
    except:
        lead_data = []        
    return lead_data    

#get the customer datas            
def get_customer(user_id,date):
    customer_data = ""
    current_date = datetime.strptime(format_date(date), "%d-%m-%Y").date()
    try:
        customer = frappe.db.sql("""
            SELECT
                name,
                DATE_FORMAT(creation, '%%d-%%m-%%Y') as formatted_date,
                TIME_FORMAT(STR_TO_DATE(creation, '%%Y-%%m-%%d %%H:%%i:%%s'), '%%H:%%i:%%s') as created_time
            FROM
                `tabCustomer`
            WHERE
                owner = %s AND
                DATE(creation) = %s
        """, (user_id,current_date), as_dict=True) or ""
        if customer:
            customer_data = customer
        else:
            customer_data = []   
    except:
        customer_data = []        
    return customer_data    
 
#get purchase Order datas
def get_purchase_order(user_id,date):
    po_data = ""
    current_date = datetime.strptime(format_date(date), "%d-%m-%Y").date()
    try:
        get_po = frappe.db.sql("""
            SELECT
                name,
                DATE_FORMAT(transaction_date, '%%d-%%m-%%Y') as date,
                TIME_FORMAT(STR_TO_DATE(creation, '%%Y-%%m-%%d %%H:%%i:%%s'), '%%H:%%i:%%s') as created_time
            FROM
                `tabPurchase Order`
            WHERE
                owner = %s AND
                DATE(creation) = %s AND docstatus != 2
        """, (user_id,current_date), as_dict=True) or ""
        if get_po:
            po_data = get_po
        else:
            po_data = []   
    except:
        po_data = []        
    return po_data
   
#get sales Order data
def get_sales_order(user_id,date):
    so_data = ""
    current_date = datetime.strptime(format_date(date), "%d-%m-%Y").date()
    try:
        get_so = frappe.db.sql("""
            SELECT
                name,
                DATE_FORMAT(transaction_date, '%%d-%%m-%%Y') as date,
                TIME_FORMAT(STR_TO_DATE(creation, '%%Y-%%m-%%d %%H:%%i:%%s'), '%%H:%%i:%%s') as created_time
            FROM
                `tabSales Order`
            WHERE
                owner = %s AND
                DATE(creation) = %s AND docstatus != 2
        """, (user_id,current_date), as_dict=True) or ""
        if get_so:
            so_data = get_so
        else:
            so_data = []   
    except:
        so_data = []        
    return so_data

#get payment entry datas
def get_payment_entry(user_id,date):
    payment_data = ""
    current_date = datetime.strptime(format_date(date), "%d-%m-%Y").date()
    try:
        payment_entry = frappe.db.sql("""
            SELECT
                name,
                DATE_FORMAT(posting_date, '%%d-%%m-%%Y') as date,
                TIME_FORMAT(STR_TO_DATE(creation, '%%Y-%%m-%%d %%H:%%i:%%s'), '%%H:%%i:%%s') as created_time
            FROM
                `tabPayment Entry`
            WHERE
                owner = %s AND
                DATE(creation) = %s AND docstatus != 2
        """, (user_id,current_date), as_dict=True) or ""
        if payment_entry:
            payment_data = payment_entry
        else:
            payment_data = []
    except:
        payment_data = []            
    return payment_data  

#get Melting Claim data
def get_melting_claim(user_id,date):
    melting_claim_data = ""
    current_date = datetime.strptime(format_date(date), "%d-%m-%Y").date()
    try:
        melting_data = frappe.db.sql("""
            SELECT
                name,
                DATE_FORMAT(posting_date, '%%d-%%m-%%Y') as date,
                TIME_FORMAT(STR_TO_DATE(creation, '%%Y-%%m-%%d %%H:%%i:%%s'), '%%H:%%i:%%s') as created_time
            FROM
                `tabMelting Claim`
            WHERE
                owner = %s AND
                DATE(creation) = %s AND docstatus != 2
        """, (user_id,current_date), as_dict=True) or ""
        if melting_data:
            melting_claim_data = melting_data
        else:
            melting_claim_data = []  
    except:
        melting_claim_data = []        
    return melting_claim_data    
      

 

      