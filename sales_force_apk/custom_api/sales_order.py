import json
import frappe
from frappe.utils import now,getdate,today,format_date,nowdate,add_months
from datetime import datetime


#create a new sales order
@frappe.whitelist()
def create_sales_order(user_id,db,outlet,date,items):
    convert_json = json.loads(items)
    status = ""
    posting_date_format = datetime.strptime(format_date(date), "%m-%d-%Y").date()
    try:
        get_user = frappe.db.exists('User',{'name':user_id,'enabled':1})
        if get_user:
            new_sales_order = frappe.new_doc('Sales Order')
            new_sales_order.company = db
            new_sales_order.customer = outlet
            new_sales_order.delivery_date = posting_date_format
            new_sales_order.transaction_date = frappe.utils.nowdate()
            for item_data in convert_json:
                new_sales_order.append("items",{
                    "item_code":item_data.get("item_code"),
                    "qty":item_data.get("qty"),
                })
            taxes_template_name = get_sales_taxes_template(db)
            if taxes_template_name:
                new_sales_order.taxes_and_charges = taxes_template_name
                taxes_template = frappe.get_doc("Sales Taxes and Charges Template", taxes_template_name)
                for tax in taxes_template.taxes:
                    new_sales_order.append("taxes", {
                        "charge_type": tax.charge_type,
                        "account_head": tax.account_head,
                        "description": tax.description,
                        "rate": tax.rate,
                    })
            new_sales_order.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Sales Order",new_sales_order.name,"owner",user_id)
            status = True
            message = "Sales Order Created Successfully"
        else:
            status = False
            message = "User has no ID or User ID Disabled"
        return {"status":status,"message":message}    
    except Exception as e:
        status = False
        return {"status": status, "message": e}

def get_sales_taxes_template(db):
    taxes = frappe.db.get_value("Sales Taxes and Charges Template",{"company":db,"tax_category":"In-State"},["name"])
    return taxes

# sales order list view 
@frappe.whitelist()
def sales_order_list(user_id):
    try:
        sales_list = frappe.get_all('Sales Order', {'owner': user_id},['*'])
        formatted_sales_list = []
        for sales_order in sales_list:
            sales_order_list = {
                "id":sales_order.name,
                "name":sales_order.name,
                "db":sales_order.company,
                "outlet":sales_order.customer,
                "posting_date":sales_order.delivery_date,
                "status":sales_order.status,
                "gross_total":sales_order.total,
                "discount":sales_order.discount_amount,
                "gst":sales_order.total_taxes_and_charges,
                "net_total":sales_order.rounded_total,
                "items":[]
            }
            items = frappe.get_all('Sales Order Item',{'parent': sales_order.name},['*'])
            sales_order['items'] = []

            for item in items:
                sales_order_list['items'].append({
                    "item_code":item.item_code,
                    "item_name":item.item_name,
                    "qty":item.qty,
                    "amount":item.amount
                })

            formatted_sales_list.append(sales_order_list)

        return {"status": True, "sales_order": formatted_sales_list}
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