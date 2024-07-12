import frappe
from frappe.utils import now,getdate,today,nowdate
from datetime import datetime


#the below code is for APK Dashboard activites page list the number of datas
@frappe.whitelist()
def dashboard_activites(user_id,db,route):
    try:
        get_user = frappe.db.exists("User",{'name':user_id})
        if get_user:
            primary_monthly_target = get_monthly_target_as_primary(user_id)
            secondary_monthly_target = get_monthly_target_as_secondary(user_id)
            primary_monthly_achieved = get_monthly_achieved_as_primary(user_id) 
            secondary_monthly_achieved = get_monthly_achieved_as_secondary(user_id)
            primary_today_achieved = get_today_achieved_as_primary(user_id)
            secondary_today_achieved = get_monthly_achieved_as_secondary(user_id)
            # Your Works Methods
            #filters using the db as company name
            if db:
                overall_lead = new_calls_overall_with_db(db)
                overall_customer = outlet_overall_with_db(db)
                overall_customer_co = overall_conversion_with_db(db)
                get_overall_active = overall_active_with_company(db)
                get_overall_inactive = overall_inactive_with_company(db)
                get_overall_pullout = overall_pullout_with_db(db)
                get_overall_complaint = overall_complaint_with_db(db)
                get_overall_dbpoint = overall_dbpoint_with_db(db)   
            else:
                overall_lead = new_calls_overall_without_db()
                overall_customer = outlet_overall_without_db()
                overall_customer_co = overall_conversion_without_db()
                get_overall_active = overall_active_without_company()
                get_overall_inactive = overall_inactive_without_company()
                get_overall_pullout = overall_pullout_without_db()
                get_overall_complaint = overall_complaint_without_db()
                get_overall_dbpoint = overall_dbpoint_without_db()
            # # #filters using the route as territory
            if route:    
                route_lead = new_calls_route_with_route(route)
                route_customer = outlet_route_with_route(route)
                route_customer_co = route_conversion_with_route(route)
                get_route_active = route_active_with_route(route)
                get_route_inactive = route_inactive_with_route(route)
                get_route_pullout = route_pullout_with_route(route)
                get_route_complaint = route_complaint_with_route(route)
                get_route_dbpoint = route_dbpoint_with_route(route)
            else:
                route_lead = new_calls_route_without_route()   
                route_customer = outlet_route_without_route()  
                route_customer_co = route_conversion_without_route()
                get_route_active = route_active_without_route()
                get_route_inactive = route_inactive_without_route()
                get_route_pullout = route_pullout_without_route()
                get_route_complaint = route_complaint_without_route()
                get_route_dbpoint = route_dbpoint_without_route()
            # #the below method only using for user_id           
            # Employee Log Type Based on Checkin
            emp_log_type = get_log_type(user_id)
        dashboard = {
            "activites":[
                {
                    "description": "Monthly Target",
                    "key":1,
                    "primary": primary_monthly_target or 0,
                    "secondary": secondary_monthly_target or 0
                },
                {
                    "description": "Monthly Achieved",
                    "key":2,
                    "primary": primary_monthly_achieved,
                    "secondary": secondary_monthly_achieved
                },
                {
                    "description": "Total Achieved",
                    "key":3,
                    "primary": primary_today_achieved,
                    "secondary": secondary_today_achieved
                }
            ],
            "your_works":[
                {
                    "description": "New Calls",
                    "key":3,
                    "overall":overall_lead,
                    "route":route_lead
                },
                {
                    "description": "Outlet",
                    "key":4,
                    "overall":overall_customer,
                    "route":route_customer
                },
                {
                    "description": "Conversion",
                    "key":5,
                    "overall":overall_customer_co,
                    "route":route_customer_co
                },
                {
                    "description": "Active",
                    "key":6,
                    "overall":get_overall_active,
                    "route":get_route_active
                },
                {
                    "description": "Inactive",
                    "key":7,
                    "overall":get_overall_inactive or 0,
                    "route":get_route_inactive or 0
                },
                {
                    "description": "Pullout",
                    "key":8,
                    "overall":get_overall_pullout,
                    "route":get_route_pullout
                },
                {
                    "description": "Complaint",
                    "key":9,
                    "overall":get_overall_complaint,
                    "route":get_route_complaint
                },
                {
                    "description": "DB Point",
                    "key":10,
                    "overall":get_overall_dbpoint,
                    "route":get_route_dbpoint
                }
            ],
            "log_type":emp_log_type
        }
        return{'status':True,'Dashboard':dashboard}
    except Exception as e:
        return {"status":False}    

#get_emp checkin log_type
def get_log_type(user_id):
    log_type = "OUT"
    get_emp = frappe.db.get_value('Employee',{'status':'Active','user_id':user_id},['name'])
    if get_emp:
        get_emp_checkin =  frappe.db.get_value('Employee Checkin',{'employee':get_emp,'custom_punch_date':getdate(today())},['log_type'])
        if get_emp_checkin:
            log_type = get_emp_checkin
        else:
            log_type = "OUT"   
    else:
        log_type = "OUT"
    return log_type        

#*get the primary monthly target in monthly target row
def get_monthly_target_as_primary(user_id):
    today = nowdate()
    query_result = ""
    get_primary_monthly_target = 0
    start_date = datetime.strptime(today, '%Y-%m-%d').month
    emp_in_user_id = frappe.db.exists("Employee",{'status':'Active','user_id':user_id})
    if emp_in_user_id:
        get_emp = frappe.db.get_value('Employee',{'name':emp_in_user_id},['designation'])
        if get_emp == "Sales Officer":
            query_result = frappe.db.sql("""
                SELECT SUM(target_amount) AS target_amount
                FROM `tabAmilma Target Setting`
                WHERE month = '%s' AND so_designation = "Sales Officer" AND type = "Primary"
            """ % (start_date), as_dict=True)
            if not query_result:
                get_primary_monthly_target = 0
            else:
                get_primary_monthly_target = query_result[0].get('target_amount', 0)         

        elif get_emp == "Area Sales Manager":
            query_result = frappe.db.sql("""
                SELECT SUM(target_amount) AS target_amount
                FROM `tabAmilma Target Setting`
                WHERE month = '%s' AND asm_designation = "Area Sales Manager" AND type = "Primary"
            """ % (start_date), as_dict=True)
            if not query_result:
                get_primary_monthly_target = 0
            else:
                get_primary_monthly_target = query_result[0].get('target_amount', 0) 

        elif get_emp == "Regional Sales Manager":
            query_result = frappe.db.sql("""
                SELECT SUM(target_amount) AS target_amount
                FROM `tabAmilma Target Setting`
                WHERE month = '%s' AND asm_designation = "Regional Sales Manager" AND type = "Primary"
            """ % (start_date), as_dict=True)
            if not query_result:
                get_primary_monthly_target = 0
            else:
                get_primary_monthly_target = query_result[0].get('target_amount', 0) 

        else:
            get_primary_monthly_target = 0
    else:
        get_primary_monthly_target = 0
        
    return get_primary_monthly_target     
   
#*get the secondary monthly target in monthly target row
def get_monthly_target_as_secondary(user_id):
    today = nowdate()
    query_result = ""
    get_secondary_monthly_target = 0
    start_date = datetime.strptime(today, '%Y-%m-%d').month
    emp_in_user_id = frappe.db.exists("Employee",{'status':'Active','user_id':user_id})
    if emp_in_user_id:
        get_emp = frappe.db.get_value('Employee',{'name':emp_in_user_id},['designation'])
        if get_emp == "Sales Officer":
            query_result = frappe.db.sql("""
                SELECT SUM(target_amount) AS target_amount
                FROM `tabAmilma Target Setting`
                WHERE month = '%s' AND so_designation = "Sales Officer" AND type = "Secondary"
            """ % (start_date), as_dict=True)
            if not query_result:
                get_secondary_monthly_target = 0
            else:
                get_secondary_monthly_target = query_result[0].get('target_amount', 0)         

        elif get_emp == "Area Sales Manager":
            query_result = frappe.db.sql("""
                SELECT SUM(target_amount) AS target_amount
                FROM `tabAmilma Target Setting`
                WHERE month = '%s' AND asm_designation = "Area Sales Manager" AND type = "Secondary"
            """ % (start_date), as_dict=True)
            if not query_result:
                get_secondary_monthly_target = 0
            else:
                get_secondary_monthly_target = query_result[0].get('target_amount', 0) 

        elif get_emp == "Regional Sales Manager":
            query_result = frappe.db.sql("""
                SELECT SUM(target_amount) AS target_amount
                FROM `tabAmilma Target Setting`
                WHERE month = '%s' AND asm_designation = "Regional Sales Manager" AND type = "Secondary"
            """ % (start_date), as_dict=True)
            if not query_result:
                get_secondary_monthly_target = 0
            else:
                get_secondary_monthly_target = query_result[0].get('target_amount', 0) 

        else:
            get_secondary_monthly_target = 0
    else:
        get_secondary_monthly_target = 0        
    return get_secondary_monthly_target

#get the monthly Achieved based on primay type
def get_monthly_achieved_as_primary(user_id):
    today = nowdate()
    query_result = ""
    get_primary_monthly_achieved = 0
    posting_start_date = frappe.utils.data.get_first_day(today)
    posting_end_date = frappe.utils.data.get_last_day(today)
    start_date = datetime.strptime(today, '%Y-%m-%d').month
    get_emp = frappe.db.exists("Employee",{'status':'Active','user_id':user_id})
    if get_emp:
        get_designation = frappe.db.get_value('Employee',{'name':get_emp},['designation'])
        if get_designation == "Sales Officer":
            get_db = frappe.db.get_value('Amilma Target Setting',{'so_designation':get_designation,'month':start_date,'type':"Primary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS monthly_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date between '%s' and '%s' AND docstatus = 1
            """ % (get_db,posting_start_date,posting_end_date), as_dict=True)
            if not query_result:
                get_primary_monthly_achieved = 0
            else:
                get_primary_monthly_achieved = query_result[0].get('rounded_total', 0) 
            
        elif get_designation == "Area Sales Manager":
            get_db = frappe.db.get_value('Amilma Target Setting',{'asm_designation':get_designation,'month':start_date,'type':"Primary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS monthly_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date between '%s' and '%s' AND docstatus = 1
            """ % (get_db,posting_start_date,posting_end_date), as_dict=True)
            if not query_result:
                get_primary_monthly_achieved = 0
            else:
                get_primary_monthly_achieved = query_result[0].get('rounded_total', 0) 
        elif get_designation == "Regional Sales Manager":
            get_db = frappe.db.get_value('Amilma Target Setting',{'rsm_designation':get_designation,'month':start_date,'type':"Primary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS monthly_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date between '%s' and '%s' AND docstatus = 1
            """ % (get_db,posting_start_date,posting_end_date), as_dict=True)
            if not query_result:
                get_primary_monthly_achieved = 0
            else:
                get_primary_monthly_achieved = query_result[0].get('rounded_total', 0)    
        else:
            get_primary_monthly_achieved = 0  
    else:
        get_primary_monthly_achieved = 0          
    return get_primary_monthly_achieved        

#get the monthly Achieved based on secondary type
def get_monthly_achieved_as_secondary(user_id):
    today = nowdate()
    query_result = ""
    get_secondary_monthly_achieved = 0
    posting_start_date = frappe.utils.data.get_first_day(today)
    posting_end_date = frappe.utils.data.get_last_day(today)
    start_date = datetime.strptime(today, '%Y-%m-%d').month
    get_emp = frappe.db.exists("Employee",{'status':'Active','user_id':user_id})
    if get_emp:
        get_designation = frappe.db.get_value('Employee',{'name':get_emp},['designation'])
        if get_designation == "Sales Officer":
            get_db = frappe.db.get_value('Amilma Target Setting',{'so_designation':get_designation,'month':start_date,'type':"Secondary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS monthly_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date between '%s' and '%s' AND docstatus = 1
            """ % (get_db,posting_start_date,posting_end_date), as_dict=True)
            if not query_result:
                get_secondary_monthly_achieved = 0
            else:
                get_secondary_monthly_achieved = query_result[0].get('rounded_total', 0) 
            
        elif get_designation == "Area Sales Manager":
            get_db = frappe.db.get_value('Amilma Target Setting',{'asm_designation':get_designation,'month':start_date,'type':"Secondary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS monthly_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date between '%s' and '%s' AND docstatus = 1
            """ % (get_db,posting_start_date,posting_end_date), as_dict=True)
            if not query_result:
                get_secondary_monthly_achieved = 0
            else:
                get_secondary_monthly_achieved = query_result[0].get('rounded_total', 0) 
        elif get_designation == "Regional Sales Manager":
            get_db = frappe.db.get_value('Amilma Target Setting',{'rsm_designation':get_designation,'month':start_date,'type':"Secondary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS monthly_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date between '%s' and '%s' AND docstatus = 1
            """ % (get_db,posting_start_date,posting_end_date), as_dict=True)
            if not query_result:
                get_secondary_monthly_achieved = 0
            else:
                get_secondary_monthly_achieved = query_result[0].get('rounded_total', 0)    
        else:
            get_secondary_monthly_achieved = 0  
    else:
        get_secondary_monthly_achieved = 0          
    return get_secondary_monthly_achieved

#get today achieved as primary
def get_today_achieved_as_primary(user_id):
    today = nowdate()
    query_result = ""
    get_today_achieved_as_primary = 0
    start_date = datetime.strptime(today, '%Y-%m-%d').month
    get_emp = frappe.db.exists("Employee",{'status':'Active','user_id':user_id})
    if get_emp:
        get_designation = frappe.db.get_value('Employee',{'name':get_emp},['designation'])
        if get_designation == "Sales Officer":
            get_db = frappe.db.get_value('Amilma Target Setting',{'so_designation':get_designation,'month':start_date,'type':"Primary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS today_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date = '%s'AND docstatus = 1
            """ % (get_db,today), as_dict=True)
            if not query_result:
                get_today_achieved_as_primary = 0
            else:
                get_today_achieved_as_primary = query_result[0].get('rounded_total', 0) 
        elif get_designation == "Area Sales Manager":
            get_db = frappe.db.get_value('Amilma Target Setting',{'asm_designation':get_designation,'month':start_date,'type':"Primary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS today_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date = '%s'AND docstatus = 1
            """ % (get_db,today), as_dict=True)
            if not query_result:
                get_today_achieved_as_primary = 0
            else:
                get_today_achieved_as_primary = query_result[0].get('rounded_total', 0)   
        elif get_designation == "Regional Sales Manager":
            get_db = frappe.db.get_value('Amilma Target Setting',{'rsm_designation':get_designation,'month':start_date,'type':"Primary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS today_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date = '%s'AND docstatus = 1
            """ % (get_db,today), as_dict=True)
            if not query_result:
                get_today_achieved_as_primary = 0
            else:
                get_today_achieved_as_primary = query_result[0].get('rounded_total', 0) 
        else:
            get_today_achieved_as_primary = 0  
    else:
        get_today_achieved_as_primary = 0  
    return get_today_achieved_as_primary

#get today achieved as secondary
def get_today_achieved_as_secondary(user_id):
    today = nowdate()
    query_result = ""
    get_today_achieved_as_secondary = 0
    start_date = datetime.strptime(today, '%Y-%m-%d').month
    get_emp = frappe.db.exists("Employee",{'status':'Active','user_id':user_id})
    if get_emp:
        get_designation = frappe.db.get_value('Employee',{'name':get_emp},['designation'])
        if get_designation == "Sales Officer":
            get_db = frappe.db.get_value('Amilma Target Setting',{'so_designation':get_designation,'month':start_date,'type':"Secondary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS today_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date = '%s'AND docstatus = 1
            """ % (get_db,today), as_dict=True)
            if not query_result:
                get_today_achieved_as_secondary = 0
            else:
                get_today_achieved_as_secondary = query_result[0].get('rounded_total', 0) 
        elif get_designation == "Area Sales Manager":
            get_db = frappe.db.get_value('Amilma Target Setting',{'asm_designation':get_designation,'month':start_date,'type':"Secondary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS today_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date = '%s'AND docstatus = 1
            """ % (get_db,today), as_dict=True)
            if not query_result:
                get_today_achieved_as_secondary = 0
            else:
                get_today_achieved_as_secondary = query_result[0].get('rounded_total', 0)   
        elif get_designation == "Regional Sales Manager":
            get_db = frappe.db.get_value('Amilma Target Setting',{'rsm_designation':get_designation,'month':start_date,'type':"Secondary"},['distributor'])
            query_result = frappe.db.sql("""
                SELECT SUM(rounded_total) AS today_achieved
                FROM `tabSales Invoice`
                WHERE customer = '%s' AND posting_date = '%s'AND docstatus = 1
            """ % (get_db,today), as_dict=True)
            if not query_result:
                get_today_achieved_as_secondary = 0
            else:
                get_today_achieved_as_secondary = query_result[0].get('rounded_total', 0) 
        else:
            get_today_achieved_as_secondary = 0  
    else:
        get_today_achieved_as_secondary = 0  
    return get_today_achieved_as_secondary

#get the overall lead count created to pass the current date and get the current month data
def new_calls_overall_with_db(db):
    overall_lead_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_leads
        FROM `tabLead`
        WHERE date(creation) BETWEEN %s AND %s AND company = %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), db), as_dict=1)
    if not query_result:
        overall_lead_count = 0
    else:
        overall_lead_count = query_result[0].get('total_leads', 0)
    return overall_lead_count

def new_calls_overall_without_db():
    overall_lead_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_leads
        FROM `tabLead`
        WHERE date(creation) BETWEEN %s AND %s 
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=1)
    if not query_result:
        overall_lead_count = 0
    else:
        overall_lead_count = query_result[0].get('total_leads', 0)
    return overall_lead_count

#get the route lead count created to pass the current date and get the current month data
def new_calls_route_with_route(route):
    route_lead_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_leads
        FROM `tabLead`
        WHERE date(creation) BETWEEN %s AND %s AND  territory = %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),route), as_dict=1)
    if not query_result:
        route_lead_count = 0
    else:
        route_lead_count = query_result[0].get('total_leads', 0)
    return route_lead_count        

def new_calls_route_without_route():
    route_lead_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_leads
        FROM `tabLead`
        WHERE date(creation) BETWEEN %s AND %s  
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=1)
    if not query_result:
        route_lead_count = 0
    else:
        route_lead_count = query_result[0].get('total_leads', 0)
    return route_lead_count     
#⁡⁢⁢⁣get the overall outlet count created to pass the current date and get the current month data
def outlet_overall_with_db(db):
    overall_outlet_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_outlet
        FROM `tabCustomer`
        WHERE date(creation) BETWEEN %s AND %s AND customer_name = %s 
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),db), as_dict=1)
    if not query_result:
        overall_outlet_count = 0
    else:
        overall_outlet_count = query_result[0].get('total_outlet', 0)
    return overall_outlet_count 

def outlet_overall_without_db():
    overall_outlet_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_outlet
        FROM `tabCustomer`
        WHERE date(creation) BETWEEN %s AND %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=1)
    if not query_result:
        overall_outlet_count = 0
    else:
        overall_outlet_count = query_result[0].get('total_outlet', 0)
    return overall_outlet_count        
   
#get the route outlet count created to pass the current date and get the current month data
def outlet_route_with_route(route):
    route_outlet_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_outlet
        FROM `tabCustomer`
        WHERE date(creation) BETWEEN %s AND %s AND  territory = %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), route), as_dict=1)   
    if not query_result:
        route_outlet_count = 0
    else:
        route_outlet_count = query_result[0].get('total_outlet', 0) 
    return route_outlet_count

def outlet_route_without_route():
    route_outlet_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_outlet
        FROM `tabCustomer`
        WHERE date(creation) BETWEEN %s AND %s 
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=1)   
    if not query_result:
        route_outlet_count = 0
    else:
        route_outlet_count = query_result[0].get('total_outlet', 0) 
    return route_outlet_count

#get the overall conversion count created to pass the current date and get the current month data
def overall_conversion_with_db(db):
    overall_conversion_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_outlet_co
        FROM `tabCustomer`
        WHERE date(creation) BETWEEN %s AND %s AND customer_name = %s AND custom_outlet_type = "CO-Conversion"
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),db), as_dict=1)
    if not query_result:
        overall_conversion_count = 0
    else:
        overall_conversion_count = query_result[0].get('total_outlet_co', 0) 
    return overall_conversion_count

def overall_conversion_without_db():
    overall_conversion_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_outlet_co
        FROM `tabCustomer`
        WHERE date(creation) BETWEEN %s AND %s AND custom_outlet_type = "CO-Conversion"
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=1)
    if not query_result:
        overall_conversion_count = 0
    else:
        overall_conversion_count = query_result[0].get('total_outlet_co', 0) 
    return overall_conversion_count

#get the route conversion count created to pass the current date and get the current month data
def route_conversion_with_route(route):
    route_conversion_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_outlet_co
        FROM `tabCustomer`
        WHERE date(creation) BETWEEN %s AND %s AND custom_outlet_type = "CO-Conversion" AND  territory = %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),route), as_dict=1)
    if not query_result:
        route_conversion_count = 0
    else:
        route_conversion_count = query_result[0].get('total_outlet_co', 0) 
    return route_conversion_count 

def route_conversion_without_route():
    route_conversion_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_outlet_co
        FROM `tabCustomer`
        WHERE date(creation) BETWEEN %s AND %s AND custom_outlet_type = "CO-Conversion"
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=1)
    if not query_result:
        route_conversion_count = 0
    else:
        route_conversion_count = query_result[0].get('total_outlet_co', 0) 
    return route_conversion_count 

# get the overall active count created to pass the current date and get the current month data
def overall_active_with_company(db):
    active_count = 0
    try:
        invoice_amount = get_overall_sales_invoice_with_company(db)
        if float(invoice_amount[0]['total']) > 2000.0:
            active_count += 1
        else:
            active_count = 0
        return active_count
    except:
        active_count = 0
        return active_count

def overall_active_without_company():
    active_count = 0
    try:
        invoice_amount = get_overall_sales_invoice_without_company()
        if float(invoice_amount[0]['total']) > 2000.0:
            active_count += 1
        else:
            active_count = 0
        return active_count
    except:
        active_count = 0
        return active_count

def overall_inactive_with_company(db):
    inactive_count = 0
    try:
        invoice_amount = get_overall_sales_invoice_with_company(db)
        if float(invoice_amount[0]['total']) < 2000.0:
            active_count += 1
        else:
            inactive_count = 0
        return inactive_count
    except:
        inactive_count = 0
        return inactive_count

def overall_inactive_without_company():
    inactive_count = 0
    try:
        invoice_amount = get_overall_sales_invoice_without_company()
        if float(invoice_amount[0]['total']) < 2000.0:
            active_count += 1
        else:
            inactive_count = 0
        return inactive_count
    except :
        inactive_count = 0
        return inactive_count

def get_overall_sales_invoice_with_company(db):
    current_date = getdate(today())
    overall_sales_invoice = 0
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COALESCE(SUM(rounded_total), 0) AS total
        FROM `tabSales Invoice`
        WHERE posting_date BETWEEN %s AND %s AND company = %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), db), as_dict=True) 
    if not query_result:
        overall_sales_invoice = 0
    else:
        overall_sales_invoice = query_result[0].get('total', 0) 
    return overall_sales_invoice

def get_overall_sales_invoice_without_company():
    current_date = getdate(today())
    overall_sales_invoice = 0
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COALESCE(SUM(rounded_total), 0) AS total
        FROM `tabSales Invoice`
        WHERE posting_date BETWEEN %s AND %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=True) 
    if not query_result:
        overall_sales_invoice = 0
    else:
        overall_sales_invoice = query_result[0].get('total', 0) 
    return overall_sales_invoice


# get the overall active count created to pass the current date and get the current month data
def route_active_with_route(route):
    active_count = 0
    get_customers = frappe.db.get_all('Customer', {'territory': route}, ['name'])
    if get_customers:
        for customer in get_customers:
            invoice_amount = get_sales_invoice_amount(customer.name)
            if float(invoice_amount[0]['total']) > 2000.0:
                active_count += 1
            else:
                active_count = 0
    else:
        active_count = 0
    return active_count 

def route_active_without_route():
    active_count = 0
    get_customers = frappe.db.get_all('Customer', ['name'])
    if get_customers:
        for customer in get_customers:
            invoice_amount = get_sales_invoice_amount(customer.name)
            if float(invoice_amount[0]['total']) > 2000.0:
                active_count += 1
            else:
                active_count = 0
    else:
        active_count = 0
    return active_count   

def route_inactive_with_route(route):
    inactive_count = 0
    get_customers = frappe.db.get_all('Customer', {'territory': route}, ['name'])
    if get_customers:
        for customer in get_customers:
            invoice_amount = get_sales_invoice_amount(customer.name)
            if float(invoice_amount[0]['total']) < 2000.0:
                inactive_count += 1
            else:
                inactive_count = 0
    else:
        inactive_count = 0
    return inactive_count            

def route_inactive_without_route():
    inactive_count = 0
    get_customers = frappe.db.get_all('Customer',['name'])
    if get_customers:
        for customer in get_customers:
            invoice_amount = get_sales_invoice_amount(customer.name)
            if float(invoice_amount[0]['total']) < 2000.0:
                inactive_count += 1
            else:
                inactive_count = 0
    else:
        inactive_count = 0
    return inactive_count             

def get_sales_invoice_amount(customer):
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)

    sales_invoice_amount = frappe.db.sql("""
        SELECT COALESCE(SUM(rounded_total), 0) AS total
        FROM `tabSales Invoice`
        WHERE posting_date BETWEEN %s AND %s AND customer = %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), customer), as_dict=True)
    return sales_invoice_amount

#get the overall_pullout status in freezer data
def overall_pullout_with_db(db):
    overall_pullout_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
    SELECT COUNT(name) AS total_pull_out
    FROM `tabFreezer Data`
    WHERE date(creation) BETWEEN %s AND %s AND status = "Pullout" AND distributor_name = %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),db),as_dict=1)
    if not query_result:
        overall_pullout_count = 0
    else:
        overall_pullout_count = query_result[0].get('total_pull_out', 0) 
    return overall_pullout_count 

def overall_pullout_without_db():
    overall_pullout_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
    SELECT COUNT(name) AS total_pull_out
    FROM `tabFreezer Data`
    WHERE date(creation) BETWEEN %s AND %s AND status = "Pullout" 
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')),as_dict=1)
    if not query_result:
        overall_pullout_count = 0
    else:
        overall_pullout_count = query_result[0].get('total_pull_out', 0) 
    return overall_pullout_count 
   
#get the route_pullout status in freezer data
def route_pullout_with_route(route):
    route_pullout_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_pull_out
        FROM `tabFreezer Data`
        WHERE date(creation) BETWEEN %s AND %s AND territory = %s AND status = "Pullout"
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),route), as_dict=1)
    if not query_result:
        route_pullout_count = 0
    else:
        route_pullout_count = query_result[0].get('total_pull_out', 0) 
    return route_pullout_count 

def route_pullout_without_route():
    route_pullout_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS total_pull_out
        FROM `tabFreezer Data`
        WHERE date(creation) BETWEEN %s AND %s  AND status = "Pullout"
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=1)
    if not query_result:
        route_pullout_count = 0
    else:
        route_pullout_count = query_result[0].get('total_pull_out', 0) 
    return route_pullout_count 

#get the overall_compliant status in freezer data
def overall_complaint_with_db(db):
    overall_compliant_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS complaint
        FROM `tabFreezer Data`
        WHERE date(creation) BETWEEN %s AND %s AND status = "Complaint" AND distributor_name = %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),db), as_dict=1)
    if not query_result:
        overall_compliant_count = 0
    else:
        overall_compliant_count = query_result[0].get('complaint', 0) 
    return overall_compliant_count 

def overall_complaint_without_db():
    overall_compliant_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS complaint
        FROM `tabFreezer Data`
        WHERE date(creation) BETWEEN %s AND %s AND status = "Complaint" 
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=1)
    if not query_result:
        overall_compliant_count = 0
    else:
        overall_compliant_count = query_result[0].get('complaint', 0) 
    return overall_compliant_count 
   
#get the route_complaint status in freezer data
def route_complaint_with_route(route):
    route_complaint_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS complaint
        FROM `tabFreezer Data`
        WHERE date(creation) BETWEEN %s AND %s AND territory = %s AND status = "Complaint"
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),route), as_dict=1)
    if not query_result:
        route_complaint_count = 0
    else:
        route_complaint_count = query_result[0].get('complaint', 0) 
    return route_complaint_count 

def route_complaint_without_route():
    route_complaint_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS complaint
        FROM `tabFreezer Data`
        WHERE date(creation) BETWEEN %s AND %s AND status = "Complaint"
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=1)
    if not query_result:
        route_complaint_count = 0
    else:
        route_complaint_count = query_result[0].get('complaint', 0) 
    return route_complaint_count 

#get the overall_dbpoint status in freezer data
def overall_dbpoint_with_db(db):
    overall_dbpoint_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS dbpoint
        FROM `tabFreezer Data`
        WHERE date(creation) BETWEEN %s AND %s AND status = "DB Point"  AND distributor_name = %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),db), as_dict=1) 
    if not query_result:
        overall_dbpoint_count = 0
    else:
        overall_dbpoint_count = query_result[0].get('dbpoint', 0) 
    return overall_dbpoint_count 

def overall_dbpoint_without_db():
    overall_dbpoint_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS dbpoint
        FROM `tabFreezer Data`
        WHERE date(creation) BETWEEN %s AND %s AND status = "DB Point" 
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=1) 
    if not query_result:
        overall_dbpoint_count = 0
    else:
        overall_dbpoint_count = query_result[0].get('dbpoint', 0) 
    return overall_dbpoint_count 
   
#get the route_dbpoint status in freezer data
def route_dbpoint_with_route(route):
    route_dbpoint_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS dbpoint
        FROM `tabFreezer Data`
        WHERE date(creation) BETWEEN %s AND %s AND territory = %s AND status = "DB Point"
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),route), as_dict=1)
    if not query_result:
        route_dbpoint_count = 0
    else:
        route_dbpoint_count = query_result[0].get('dbpoint', 0) 
    return route_dbpoint_count 

def route_dbpoint_without_route():
    route_dbpoint_count = 0
    query_result = ""
    current_date = getdate(today())
    start_date = frappe.utils.data.get_first_day(current_date)
    end_date = frappe.utils.data.get_last_day(current_date)
    query_result = frappe.db.sql("""
        SELECT COUNT(name) AS dbpoint
        FROM `tabFreezer Data`
        WHERE date(creation) BETWEEN %s AND %s AND status = "DB Point"
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')), as_dict=1)
    if not query_result:
        route_dbpoint_count = 0
    else:
        route_dbpoint_count = query_result[0].get('dbpoint', 0) 
    return route_dbpoint_count 