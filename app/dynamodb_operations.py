from calendar import c
from cgi import print_arguments
import requests
import json
from werkzeug.security import generate_password_hash
url = '*' #Need to set by your self when running
user_url = '*' #Need to set by your self when running
def register(info:dict):
    headers = {"Content-Type":"application/json"}
    #should be a check for email
    check_result = check_user_by_email(info["email"])
    if check_result == 200:
        data = {"email":info["email"]}
        passwd_hash = generate_password_hash(info["password"],method='pbkdf2:sha512')
        data["passwd_hash"] = passwd_hash
        data_input = json.dumps(data)
        r = requests.put(user_url, headers=headers,data = data_input)
        if r.status_code == 200:
            return True
        else:
            print(f"Error, with error message:{r.text}")
            return False
    elif check_result == 400:
        return "User Exists"
    else:
        return "Internet Connection Error"
def update_password(info:dict)->bool:
    headers = {"Content-Type":"application/json"}
    passwd_hash = generate_password_hash(info["password"],method='pbkdf2:sha512')
    update_url = user_url+"/update/password/"+info["id"]
    data = {"id":info["id"],
            "passwd_hash":passwd_hash }
   
    data_input = json.dumps(data)
    r = requests.put(update_url, headers=headers,data = data_input)
    if r.status_code == 200:
        return True
    else:
        print(f"Error, with error message:{r.text}")
        return False
def find_user_by_email(email:str)->dict:
    get_url = user_url+"/email/"+email
    r = requests.request("GET",get_url)
    if r.status_code == 200:
        item = json.loads(r.content)
        #print(item)
        if item["Count"] == 0:
            return {} 
        user = item["Items"][0]
        info = {"email":user["email"], 
                "passwd_hash":user["passwd_hash"],
                "userid":user["userid"]}
        if "username" in user:
            info["username"] = user["username"]
        if "admin_no" in user:
            info["admin_no"] = user["admin_no"]
        return info
    else:
        print(f"Error, with error message:{r.text}")
        return None
def find_user_by_id(id:str)->dict:
    get_url = user_url+"/"+id
    r = requests.request("GET",get_url)
    if r.status_code == 200:
        item = json.loads(r.content)
        #print(item)
        if item == {}:
            return item

        user = item["Item"]
        info = {"email":user["email"], 
                "passwd_hash":user["passwd_hash"],
                "userid":user["userid"]}
        if "username" in user:
            info["username"] = user["username"]
        if "admin_no" in user:
            info["admin_no"] = user["admin_no"]
        return info
    else:
        print(f"Error, with error message:{r.text}")
        return None
def check_user_by_email(email:str)->int:
    get_url = user_url+"/email/"+email
    r = requests.request("GET",get_url)
    if r.status_code == 200:
        item = json.loads(r.content)
        #print(item)
        count = item["Count"]
        if count == 0:
            return 200
        else:
            return 400
    else:
        print(f"Error, with error message:{r.text}")
        return 404
def add_resident(info:tuple)->bool:
    headers = {"Content-Type":"application/json"}
    data = {"id":info["id"],
            "name":info["name"],
            "email":info["email"] }
    dose_number = 0
    if info["phone_number"] != "":
        data["phone_number"] = info["phone_number"]
    if info["vaccine_type_1"] != "":
        data["vaccine_type_1"] = info["vaccine_type_1"]
        data["vaccine_date_1"] = info["vaccine_date_1"]
        dose_number += 1
    if info["vaccine_type_2"] != "":
        data["vaccine_type_2"] = info["vaccine_type_2"]
        data["vaccine_date_2"] = info["vaccine_date_2"]
        dose_number += 1
    if info["vaccine_type_3"] != "":
        data["vaccine_type_3"] = info["vaccine_type_3"]
        data["vaccine_date_3"] = info["vaccine_date_3"]
        dose_number += 1
    data["dose_number"] = str(dose_number)
    data_input = json.dumps(data)
    r = requests.put(url, headers=headers,data = data_input)
    if r.status_code == 200:
        return True
    else:
        print(f"Error, with error message:{r.text}")
        return False
def update_resident(info:tuple)->bool:
    headers = {"Content-Type":"application/json"}
    update_url = url+"/update/"+info["id"]
    data = {"id":info["id"],
            "name":info["name"],
            "email":info["email"] }
    dose_number = 0
    
    # if info["phone_number"] != "":
    
    data["phone_number"] = info["phone_number"]
    data["vaccine_type_1"] = info["vaccine_type_1"]
    data["vaccine_date_1"] = info["vaccine_date_1"]
    data["vaccine_type_2"] = info["vaccine_type_2"]
    data["vaccine_date_2"] = info["vaccine_date_2"]
    data["vaccine_type_3"] = info["vaccine_type_3"]
    data["vaccine_date_3"] = info["vaccine_date_3"]
    if info["vaccine_type_1"] != "":
        # data["vaccine_type_1"] = info["vaccine_type_1"]
        # data["vaccine_date_1"] = info["vaccine_date_1"]
        dose_number += 1
    if info["vaccine_type_2"] != "":
        # data["vaccine_type_2"] = info["vaccine_type_2"]
        # data["vaccine_date_2"] = info["vaccine_date_2"]
        dose_number += 1
    if info["vaccine_type_3"] != "":
        # data["vaccine_type_3"] = info["vaccine_type_3"]
        # data["vaccine_date_3"] = info["vaccine_date_3"]
        dose_number += 1
    data["dose_number"] = str(dose_number)
    data_input = json.dumps(data)
    r = requests.put(update_url, headers=headers,data = data_input)
    if r.status_code == 200:
        return True
    else:
        print(f"Error, with error message:{r.text}")
        return False
def delete_resident(residentid:str)->bool:
    del_url = url+"/"+residentid
    r = requests.request("DELETE",del_url)
    if r.status_code == 200:
        return True
    else:
        print(f"Error, with error message:{r.text}")
        return False
def get_one_resident(residentid:str)->dict:
    get_url = url+"/"+residentid
    r = requests.request("GET",get_url)
    if r.status_code == 200:
        
        item = json.loads(r.content)
        if item == {}:
            return {}
        resident = item["Item"]
        #does = 0
        info = {"name":resident["name"],
           "email":resident["email"] }
        print(resident)
        if "phone_number" in resident:
            info["phone_number"] = resident["phone_number"]
        else:
            info["phone_number"] = ""

        if "vaccine_type_1" in resident:
            info["vaccine_type_1"] = resident["vaccine_type_1"]
            info["vaccine_date_1"] = resident["vaccine_date_1"]
            #does += 1
        else:
            info["vaccine_type_1"] = ""
            info["vaccine_date_1"] = ""

        if "vaccine_type_2" in resident:
            info["vaccine_type_2"] = resident["vaccine_type_2"]
            info["vaccine_date_2"] = resident["vaccine_date_2"]
            #does += 1
        else:
            info["vaccine_type_2"] = ""
            info["vaccine_date_2"] = ""

        if "vaccine_type_3" in resident:
            info["vaccine_type_3"] = resident["vaccine_type_3"]
            info["vaccine_date_3"] = resident["vaccine_date_3"]
            #does += 1
        else:
            info["vaccine_type_3"] = ""
            info["vaccine_date_3"] = ""

        if "admin_no" in resident:
            info["admin_no"] = resident["admin_no"]
            
        if "dose_number" in resident:
            info['dose_number'] = resident['dose_number']
        else:
            info['dose_number'] = ""
        #print(item["Item"]["name"])
        return info
    else:
        print(f"Error, with error message:{r.text}")
        return {}
def get_all_residents()->list:
    get_all_url = url+"/users"
    r = requests.request("GET",get_all_url)
    if r.status_code == 200:
        
        item = json.loads(r.content)
        #print(item)
        if item["Count"] == 0:
            return []
        residents = item["Items"]
        return residents
    else:
        print(f"Error, with error message:{r.text}")
        return []
def get_resident_doses(id)-> str:
    get_doses_url = url+"/doses/"+id
    r = requests.request("GET",get_doses_url)
    if r.status_code == 200:
        item = json.loads(r.content)
        if item == {}:
            return "Not found"
        else:
            dose_info = item["Item"]
            if "dose_number" in dose_info:
                return dose_info["dose_number"]
            else:
                print("Don't have any doses yet")
                return None
    else:
        return "connection error"
def get_image_status(id)-> str:
    get_image_url = url+"/image_status/"+id
    r = requests.request("GET",get_image_url)
    if r.status_code == 200:
        item = json.loads(r.content)
        if item == {}:
            return "Not found"
        else:
            image_info = item["Item"]
            if "image_status" in image_info:
                return image_info["image_status"]
            else:
                print("Don't have any doses yet")
                return "0"
    else:
        return "connection error"
def set_image_status_code(id, image_status)->str:
    image_url = url+"/update/"+"image_status"
    headers = {"Content-Type":"application/json"}
    data = {"id":id,"image_status":image_status}
    data_input = json.dumps(data)
    r = requests.put(image_url, headers=headers,data = data_input)
    if r.status_code == 200:
        return True
    else:
        print(f"Error, with error message:{r.text}")
        return False