import frappe
import base64
from frappe.utils.file_manager import save_file


@frappe.whitelist()
def create_new_call_as_lead(user_id,db,outlet_name,owner_name,outlet_category,route,address,mobile_number,daily_sales,
                        existing_brand,ice_cream_sales,shop_inside_image,shop_outside_image,
                        latitude, longitude, live_location):
    message = ""
    status = ""
    try:
        get_user = frappe.db.exists('User',{'name':user_id,'enabled':1})
        if get_user:
            decoded_data_inside = base64.b64decode((shop_inside_image))
            decoded_data_outside = base64.b64decode((shop_outside_image))
            
            new_lead = frappe.get_doc({
                'doctype':'Lead',
                'customer_group':db,
                'first_name':outlet_name,
                'company_name':owner_name,
                'custom_outlet_category':outlet_category,
                'territory':route,
                'custom_outlet_address':address,
                'phone':mobile_number,
                'shop_daily_sales':daily_sales,
                'custom_existing_ice_cream_brand':existing_brand,
                'ice_cream_sales':ice_cream_sales,
                'custom_latitude':latitude,
                'custom_latitude':longitude,
                'custom_live_location':live_location
            })
            new_lead.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value('Lead',new_lead.name,'owner',user_id)
            
            file_name_inside = f"{new_lead.name.replace(' ', '_')}_image.png"
            new_file_inside = frappe.new_doc('File')
            new_file_inside.file_name = file_name_inside
            new_file_inside.content = decoded_data_inside
            new_file_inside.attached_to_doctype = "Lead"
            new_file_inside.attached_to_name = new_lead.name
            new_file_inside.attached_to_field = "custom_shop_inside_image"
            new_file_inside.is_private = 0
            new_file_inside.save(ignore_permissions=True)
            frappe.db.commit()

            frappe.db.set_value('Lead',new_lead.name,'custom_shop_inside_image',new_file_inside.file_url)
            
            file_name_outside = f"{new_lead.name.replace(' ', '_')}_image.png"
            new_file_outside = frappe.new_doc('File')
            new_file_outside.file_name = file_name_outside
            new_file_outside.content = decoded_data_outside
            new_file_outside.attached_to_doctype = "Lead"
            new_file_outside.attached_to_name = new_lead.name
            new_file_outside.attached_to_field = "custom_shop_outside_image"
            new_file_outside.is_private = 0
            new_file_outside.save(ignore_permissions=True)
            frappe.db.commit()

            frappe.db.set_value('Lead',new_lead.name,'custom_shop_outside_image',new_file_outside.file_url)
            status = True
            message = "New Call Created Successfully"
        else:
            message = "Employee have no record" 
        return {"status":status,"message":message}
    except:
        return {"status":status}

# new_call list view
@frappe.whitelist()
def lead_list(user_id):
    try:
        # Fetch Leads based on owner
        leads = frappe.db.get_all('Lead', {'owner': user_id},['*'])
        formatted_lead_list = []
        for lead in leads:
            lead_data = {
                'id':lead.name,
                'name':lead.name,
                'customer_group': lead.customer_group,
                'outlet_name': lead.first_name,
                'owner_name': lead.company_name,
                'outlet_category': lead.custom_outlet_category,
                'route': lead.territory,
                'address': lead.custom_outlet_address,
                'mobile_number': lead.phone,
                'daily_sales': lead.shop_daily_sales,
                'existing_brand': lead.custom_existing_ice_cream_brand,
                'ice_cream_sales': lead.ice_cream_sales,
                'live_location': lead.custom_live_location
            }
            
            formatted_lead_list.append(lead_data)
        return {"status": True, "lead": formatted_lead_list}
    except:
        return {"status": False}

    