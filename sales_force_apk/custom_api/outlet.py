import frappe
from frappe.utils import now,getdate,today,format_date
from datetime import datetime
import base64

@frappe.whitelist()
def create_new_outlet_as_customer(user_id,db,route,customer_name,joining_year,area_sales_manager,outlet_address,personal_address,customer_joining_date,
                                  outlet_name,outlet_category,outlet_type,shop_daily_sales,existing_brand,ice_cream_sales,  
                                  owner_name,father_name,email_id,mobile_number,aadhar_number,alternate_number,
                                  freezer_data,mode_of_payment,transaction_number,freezer_date,latitude, longitude, live_location,shop_inside_image,shop_outside_image):
    address = ""
    message = ""
    status = ""
    try:
        get_user = frappe.db.exists('User',{'name':user_id,'enabled':1})
        if get_user:
            #decoding the base64 and convert into a image file url
            decoded_data_inside = base64.b64decode((shop_inside_image))
            decoded_data_outside = base64.b64decode((shop_outside_image))
        
            #formatting the date
            joining_date_format = datetime.strptime(format_date(customer_joining_date), "%m-%d-%Y").date()
            freezer_date_format = datetime.strptime(format_date(freezer_date), "%m-%d-%Y").date()
            
            #the below code is check the customer group in database
            if frappe.db.exists("Customer Group",{"name":db}):
                customer_group = db
            else:
                status = False
                # message = "is not in db"
                message = f"{db} is not in database"
            # the below code is check the route in database
            if frappe.db.exists("Territory",{"name":route}):
                territory = route
            else:
                status = False
                message = f"{route} is not in database"

            # the below code is check the sales manager in database
            if frappe.db.exists("Sales Partner",{"name":area_sales_manager}):
                area_manager = area_sales_manager
            else:
                status = False
                message = f"{area_sales_manager} is not in database"

            # the below code is check the outlet category in database
            if frappe.db.exists("Outlet Category",{"name":outlet_category}):
                outlet_cat = outlet_category
            else:
                status = False
                message = f"{outlet_category} is not in database"

            # the below code is check the outlet type in database
            if frappe.db.exists("Outlet Type",{"name":outlet_type}):
                outlet_type_customer = outlet_type
            else:
                status = False
                message = f"{outlet_type} is not in database"

            # the below code is check the Existing Brand  in database
            if frappe.db.exists("Existing Brand and Volume",{"name":existing_brand}):
                existing_brand_customer = existing_brand
            else:
                status = False
                message = f"{existing_brand} is not in database"

            # the below code is check the freezer data in database
            if frappe.db.exists("Freezer Data",{"name":freezer_data}):
                freezer = freezer_data
            else:
                status = False
                message = f"{freezer_data} is not in database"  
            
            # the below code is check the mode of payment in database
            if frappe.db.exists("Mode of Payment",{"name":mode_of_payment}):
                payment_mode = mode_of_payment
            else:
                status = False
                message = f"{mode_of_payment} is not in database"


            customer_name_already_exists = frappe.db.exists("Customer",{'customer_name':customer_name})
            if not customer_name_already_exists:
                new_outlet = frappe.get_doc({
                    'doctype':'Customer',
                    'customer_group':customer_group,  
                    'territory':territory,  
                    'default_price_list': "Standard Selling",
                    'joining_date_abbr':joining_year,
                    'default_sales_partner':area_manager,
                    'custom_customer_joining_date':joining_date_format,
                    'custom_outlet_name':outlet_name,
                    'custom_outlet_category':outlet_cat,
                    'custom_outlet_type':outlet_type_customer,
                    'custom_shop_daily_sales':shop_daily_sales,
                    'custom_existing_brand':existing_brand_customer,
                    'custom_ice_cream_sales':ice_cream_sales,
                    'customer_name':customer_name,
                    'freezer_data':freezer,
                    'custom_latitude':latitude,
                    'custom_longitude':longitude,
                    'custom_live_location':live_location
                })
                new_outlet.insert(ignore_permissions=True)
                frappe.db.commit()
                frappe.db.set_value('Customer',new_outlet.name,'owner',user_id)
                status = True
                message = "Customer Created"

                #base64 to image ship_inside_image
                if shop_inside_image:
                    file_name_inside = f"{new_outlet.name.replace(' ', '_')}_image.png"
                    new_file_inside = frappe.new_doc('File')
                    new_file_inside.file_name = file_name_inside
                    new_file_inside.content = decoded_data_inside
                    new_file_inside.attached_to_doctype = "Customer"
                    new_file_inside.attached_to_name = new_outlet.name
                    new_file_inside.attached_to_field = "custom_shop_inside_image"
                    new_file_inside.is_private = 0
                    new_file_inside.save(ignore_permissions=True)
                    frappe.db.commit()
                    frappe.db.set_value('Customer',new_outlet.name,'custom_shop_inside_image',new_file_inside.file_url)

                #shop_outside_image
                if shop_outside_image:
                    file_name_outside = f"{new_outlet.name.replace(' ', '_')}_image.png"
                    new_file_outside = frappe.new_doc('File')
                    new_file_outside.file_name = file_name_outside
                    new_file_outside.content = decoded_data_outside
                    new_file_outside.attached_to_doctype = "Customer"
                    new_file_outside.attached_to_name = new_outlet.name
                    new_file_outside.attached_to_field = "custom_shop_outside_image"
                    new_file_outside.is_private = 0
                    new_file_outside.save(ignore_permissions=True)
                    frappe.db.commit()
                    frappe.db.set_value('Customer',new_outlet.name,'custom_shop_outside_image',new_file_outside.file_url) 

                ##create outlet_Address
                split_address = outlet_address.split(',')
                address = frappe.new_doc('Address')
                address.address_title = new_outlet.name
                address.address_type = "Billing"
                address.address_line1 = outlet_address
                split_city = split_address[-1].split('-')
                address.city = split_city[0]
                address.pincode = split_city[-1]
                address_child_table = address.append('links',{})
                address_child_table.link_doctype = "Customer"
                address_child_table.link_name = new_outlet.name
                address.insert(ignore_permissions=True)
                frappe.db.commit()

                #create address for contact
                split_address = personal_address.split(',')
                pers_addrs = frappe.new_doc('Address')
                pers_addrs.address_title = owner_name
                pers_addrs.address_type = "Personal"
                pers_addrs.address_line1 = personal_address
                split_city = split_address[-1].split('-')
                pers_addrs.city = split_city[0]
                pers_addrs.pincode = split_city[-1]
                pers_addrs.phone = alternate_number
                pers_addrs.insert(ignore_permissions=True)
                frappe.db.commit()

                #create contact for personal details
                contact = frappe.new_doc('Contact')
                contact.first_name = owner_name
                contact.custom_father_guardian_name = father_name
                contact.custom_aaadhar_number = aadhar_number
                contact.address = pers_addrs.name
                email_child_table = contact.append('email_ids',{})
                email_child_table.email_id = email_id
                number_child_table = contact.append('phone_nos',{})
                number_child_table.phone = mobile_number
                link_child_table = contact.append('links',{})
                link_child_table.link_doctype = "Customer"
                link_child_table.link_name = new_outlet.name
                contact.save(ignore_permissions=True)
                frappe.db.commit()

                #update the freezer transaction number and date
                update_freezer = frappe.get_doc('Freezer Data',{'name':freezer_data})
                update_freezer.mode_of_payment = payment_mode
                update_freezer.transaction_reference_number = transaction_number
                update_freezer.freezer_placed_date = freezer_date_format
                update_freezer.save(ignore_permissions=True)
                frappe.db.commit()
            else:
                status = False  
                message = "Already in Customer"  
        else:
            message = "Employee have no record" 
        return {"status":status,"message":message}
    except:
        return {"status":status,"message":message}
    
   
# customer list view 
@frappe.whitelist()
def outlet_list(user_id):
    try:
        get_customer = frappe.get_all('Customer', {'owner': user_id}, ['name','customer_name','customer_group','territory','custom_outlet_name','custom_outlet_category','joining_date_abbr',
                                                                    'custom_customer_joining_date','custom_live_location','custom_outlet_type','custom_shop_daily_sales',
                                                                    'custom_existing_brand','custom_ice_cream_sales'])

        outlet_data = []

        for outlet in get_customer:
            frezzer_data = frappe.db.get_all('Freezer Data',{'dealer':outlet['name']},['name','make','model','capacity','basket','serial_no','freezer_deposit_status','freezer_deposit','mode_of_payment','transaction_reference_number','freezer_placed_date'])
            if frezzer_data:
                frezzer_data_list = frezzer_data
            else:
                frezzer_data_list = ""    
            get_address_list = get_outlet_address(outlet.name)
            get_personal_address_list = get_personal_address(outlet.name)
            outlet_list = {
                "id": outlet['name'] or "",
                "name":outlet['name'] or "",
                "customer_name":outlet['customer_name'],
                "db":outlet['customer_group'] or "",
                "route":outlet['territory'],
                "outlet_name":outlet['custom_outlet_name'] or "",
                "outlet_category":outlet['custom_outlet_category'] or "",
                "joining_year":outlet['joining_date_abbr'] or "",
                "customer_joining_date":format_date(outlet['custom_customer_joining_date']) or "",
                "gps_location":outlet['custom_live_location'] or "",
                "outlet_type":outlet['custom_outlet_type'] or "",
                "shop_daily_sales":outlet['custom_shop_daily_sales'] or "",
                "existing_brand":outlet['custom_existing_brand'] or "",
                "ice_cream_sales":outlet['custom_ice_cream_sales'] or "",
                "frezzer_data":frezzer_data_list or "",
                "outlet_address":get_address_list or "",
                "personal_address":get_personal_address_list or ""
            }
            outlet_data.append(outlet_list)

        return {"status": True, "outlet_list": outlet_data}
    except :
        return {"status": False}



def get_outlet_address(customer_id):
    get_address = frappe.db.get_all('Address',{'address_type':"Billing"},['*'])
    for address in get_address:
        get_link_doctypes = frappe.db.get_all('Dynamic Link',{'parent':address.name},['*'])
        for link_doctype in get_link_doctypes:
            if link_doctype.link_doctype == "Customer":
                if link_doctype.link_name == customer_id:
                    if address.address_type == "Billing":
                        address_list = {
                            "address_line1":address.address_line1,
                            "address_line2":address.address_line2,
                            "city":address.city,
                            "phone":address.phone
                        }
                        return address_list


def get_personal_address(customer_id):
    get_contact = frappe.db.get_all('Contact',{},['*'])
    for contact in get_contact:
        get_link_doctypes = frappe.db.get_all('Dynamic Link',{'parent':contact.name},['*'])
        for link_doctype in get_link_doctypes:
            if link_doctype.link_doctype == "Customer":
                if link_doctype.link_name == customer_id:
                    address = contact.address
                    personal_address = frappe.get_doc('Address',{'name':address})
                    personal_address_list = {
                        "address_line1":personal_address.address_line1,
                        "address_line2":personal_address.address_line2,
                        "city":personal_address.city,
                        "phone":personal_address.phone
                    }
                    return personal_address_list
