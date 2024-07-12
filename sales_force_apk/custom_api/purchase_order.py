import frappe
from frappe.utils import now,getdate,today,format_date
from datetime import datetime
import json


#create a new purchase order
@frappe.whitelist()
def create_purchase_order(user_id,db,date,items):
    convert_json = json.loads(items)
    status = ""
    posting_date_format = datetime.strptime(format_date(date), "%m-%d-%Y").date()
    try:
        get_user = frappe.db.exists('User',{'name':user_id,'enabled':1})
        if get_user:
            new_purchase_order = frappe.new_doc('Purchase Order')
            new_purchase_order.company = db
            new_purchase_order.supplier = "Sree Amoha Food Gallery Pvt Ltd"
            new_purchase_order.transaction_date = posting_date_format
            new_purchase_order.schedule_date = posting_date_format
            for item_data in convert_json:
                new_purchase_order.append("items",{
                    "item_code":item_data.get("item_code"),
                    "qty":item_data.get("qty"),
                })
            taxes_template_name = get_purchase_taxes_template(db)       
            if taxes_template_name:
                new_purchase_order.taxes_and_charges = taxes_template_name
                taxes_template = frappe.get_doc("Purchase Taxes and Charges Template", taxes_template_name)
                for tax in taxes_template.taxes:
                    new_purchase_order.append("taxes", {
                        "charge_type": tax.charge_type,
                        "account_head": tax.account_head,
                        "description": tax.description,
                        "rate": tax.rate,
                    })    
            new_purchase_order.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Purchase Order",new_purchase_order.name,"owner",user_id)
            status = True
            message = "Purchase Order Created Successfully"
        else:
            status = False
            message = "User has no ID or User ID Disabled"
        return {"status":status,"message":message}    
    except Exception as e:
        status = False
        return {"status": status, "message": e}

def get_purchase_taxes_template(db):
    taxes = frappe.db.get_value("Purchase Taxes and Charges Template",{"company":db,"tax_category":"In-State"},["name"])
    return taxes

# Purchase order list view 
@frappe.whitelist()
def purchase_order_list(user_id):
	try:
		purchase_list = frappe.get_all('Purchase Order',{'owner': user_id},['*'])

		formatted_purchase_list = []
		
		for purchase_order in purchase_list:
			purchase_order_list = {
                "id":purchase_order.name,
                "name":purchase_order.name,
                "db":purchase_order.company,
				"posting_date":purchase_order.schedule_date,
                "status":purchase_order.status,
                "gross_total":purchase_order.total,
                "discount":purchase_order.discount_amount,
                "gst":purchase_order.total_taxes_and_charges,
                "net_total":purchase_order.rounded_total,
                "items":[]
            }
			items = frappe.get_all('Purchase Order Item',{'parent': purchase_order.name},['*'])
			purchase_order['items'] = []
		
			for item in items:
				purchase_order_list['items'].append({
                    "item_code":item.item_code,
                    "item_name":item.item_name,
                    "qty":item.qty,
                    "amount":item.amount
                })
			
			formatted_purchase_list.append(purchase_order_list)

		return {"status": True, "Purchase_Order": formatted_purchase_list}
	except:
		return {"status": False}


