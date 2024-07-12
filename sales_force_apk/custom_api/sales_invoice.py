import frappe
from frappe.utils import now,getdate,today,format_date,nowdate,add_months,formatdate


@frappe.whitelist()
def get_sales_id(db,outlet):
    status = ""
    try:
        get_sales_invoice =frappe.db.sql("""SELECT name as id,DATE_FORMAT(posting_date, '%%d-%%m-%%Y') as date,rounded_total as invoice_amount FROM `tabSales Invoice`WHERE company = '%s'
                                        AND customer = '%s' AND status != 'Paid' AND docstatus = 1"""%(db,outlet),as_dict=1)
        status = True
        return {"status":status,"sales_invoice":get_sales_invoice}
    except Exception as e:
        status = False    
        return {"status":status,"message":e}