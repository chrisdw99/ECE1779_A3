import base64
from cmath import inf
from crypt import methods
from errno import ESTALE
from gettext import find
from flask import redirect, render_template, request, flash, url_for
from werkzeug.utils import secure_filename
from app import dynamodb_operations as dy_ope
import io
from app import webapp
#from app import database_operations as db_ope
import requests
import boto3
import app
import re
from flask_login import current_user

#ta = boto3.session.Session(profile_name='default')
s3 = boto3.resource('*') #replace with your own s3 profile
bucket = s3.Bucket(name='*')#replace with your own s3 bucket
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
status_code_dic = {"0":"1","1":"2","2":"1","3":"3","4":"1","5":"2","6":"1"}
status_code_add = {"0":"1","1":"3","2":"3","3":"7","4":"5","5":"7","6":"7"}
status_code_del=   {("1","1"):"0",("1","3"):"2",("1","5"):"4",("1","7"):"6",
                    ("2","2"):"0",("2","3"):"1",("2","6"):"4",("2","7"):"5",
                    ("3","4"):"0",("3","5"):"1",("3","6"):"2",("3","7"):"3"}
status_abnormal = (-99, -99)
status_cannot_upload=(-98, -98)

@webapp.route('/search_key', methods=['POST'])
def search_key():
    name=request.form.get('name', "")
    return render_template("search_resident.html")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_as_en(file_bytes):
    textract = boto3.client('textract', region_name="us-east-1")
    response = textract.detect_document_text(Document={'Bytes': file_bytes})

    resident_info=init_resident_info_from_image()
    vaccine_type = ""
    vaccine_date = ""
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            text = translate_to_en(item["Text"])
            find_resident_info(resident_info, 'name', 'Name', text)
            find_resident_info(resident_info, 'phone_number', 'Phone Number', text)
            find_resident_info(resident_info, 'email', 'E-mail', text)
            vaccine_type = find_vaccine_info('Product Name', text, vaccine_type)
            vaccine_date = find_vaccine_info('Date/Date', text, vaccine_date)
            find_doses_number(resident_info, text)
    fill_vaccine_info(resident_info, vaccine_type, vaccine_date)
    return resident_info

def translate_to_en(text):
    translate  = boto3.client('translate', region_name="us-east-1")
    response = translate.translate_text(
        Text=text,
        SourceLanguageCode='auto',
        TargetLanguageCode='en',
    )
    return(response.get('TranslatedText')) 

def init_resident_info(userid):
    resident_info=dy_ope.get_one_resident(userid)
    if resident_info == {}:
        resident_info['name'] = ""
        resident_info['phone_number'] = ""
        resident_info['email'] = ""
        resident_info['vaccine_type_1'] = ""
        resident_info['vaccine_date_1'] = ""
        resident_info['vaccine_type_2'] = ""
        resident_info['vaccine_date_2'] = ""
        resident_info['vaccine_type_3'] = ""
        resident_info['vaccine_date_3'] = ""
        resident_info['doses_number'] = ""
    return resident_info

def init_resident_info_from_image():
    resident_info = {}
    resident_info['name'] = ""
    resident_info['phone_number'] = ""
    resident_info['email'] = ""
    resident_info['vaccine_type_1'] = ""
    resident_info['vaccine_date_1'] = ""
    resident_info['vaccine_type_2'] = ""
    resident_info['vaccine_date_2'] = ""
    resident_info['vaccine_type_3'] = ""
    resident_info['vaccine_date_3'] = ""
    resident_info['doses_number'] = ""
    return resident_info

def find_resident_info(resident_info, key, filter, text):
    if filter in text:
        if resident_info[key] == "":
            resident_info[key] = text.rsplit(": ", 1)[1]

def find_doses_number(resident_info, text):
    if "You have received" in text:
        if resident_info['doses_number'] == "":
            resident_info['doses_number'] = re.findall('[0-9]+', text)[0]

def find_vaccine_info(filter, text, container):
    if container == "":
        result = ""
        if filter in text:
            result = text.rsplit(": ", 1)[1]
        if filter == 'Date/Date':
            result = result.rsplit(",", 1)[0]
        return result
    else:
        return container

def fill_vaccine_info(resident_info, vaccine_type, vaccine_date):
    doses_number = resident_info['doses_number']
    if doses_number == "1":
        resident_info['vaccine_type_1'] = vaccine_type
        resident_info['vaccine_date_1'] = vaccine_date
    elif doses_number == "2":
        resident_info['vaccine_type_2'] = vaccine_type
        resident_info['vaccine_date_2'] = vaccine_date
    elif doses_number == "3":
        resident_info['vaccine_type_3'] = vaccine_type
        resident_info['vaccine_date_3'] = vaccine_date

def detect_doses_numner(resident_info, info):
    doses_number = ""
    # print(resident_info)
    # print(info)
    if (info['vaccine_type_1'] != resident_info['vaccine_type_1'] or info['vaccine_date_1'] != resident_info['vaccine_date_1']) and (info['vaccine_type_1']!="" or info['vaccine_date_1']!=""):
        doses_number = "1"
    elif info['vaccine_type_2'] != resident_info['vaccine_type_2'] or info['vaccine_date_2'] != resident_info['vaccine_date_2'] and (info['vaccine_type_2']!="" or info['vaccine_date_2']!=""):
        doses_number = "2"
    elif info['vaccine_type_3'] != resident_info['vaccine_type_3'] or info['vaccine_date_3'] != resident_info['vaccine_date_3'] and (info['vaccine_type_3']!="" or info['vaccine_date_3']!=""):
        doses_number = "3"
    
    if doses_number == "":
        if info['vaccine_type_1']!="" and info['vaccine_date_1']!="":
            doses_number = "1"
        elif info['vaccine_type_2']!="" and info['vaccine_date_2']!="":
            doses_number = "2"
        elif info['vaccine_type_3']!="" and info['vaccine_date_3']!="":
            doses_number = "3"

    return doses_number

def is_resident_info_empty(resident_info):
    if resident_info['name'] == "" and resident_info['phone_number'] == "" and resident_info['email'] == "" \
        and resident_info['vaccine_type_1'] == "" and resident_info['vaccine_date_1'] == "" \
        and resident_info['vaccine_type_2'] == "" and resident_info['vaccine_date_2'] == "" \
        and resident_info['vaccine_type_3'] == "" and resident_info['vaccine_date_3'] == "" \
        and resident_info['doses_number'] == "":
        return True
    else:
        return False
def is_resident_info_completed(resident_info):
    if resident_info['name'] != "" and resident_info['phone_number'] != "" and resident_info['email'] != "" \
        and (not((resident_info['vaccine_type_1'] != "") ^ (resident_info['vaccine_date_1'] != "")) \
        and not((resident_info['vaccine_type_2'] != "") ^ (resident_info['vaccine_date_2'] != "")) \
        and not((resident_info['vaccine_type_3'] != "") ^ (resident_info['vaccine_date_3'] != "")))\
        and not(resident_info['vaccine_type_1'] == "" and resident_info['vaccine_date_1'] == "" \
        and resident_info['vaccine_type_2'] == "" and resident_info['vaccine_date_2'] == "" \
        and resident_info['vaccine_type_3'] == "" and resident_info['vaccine_date_3'] == ""):
        return True
    else:
        return False

def upload_img_to_s3(img_bytes, filename):
    bucket.upload_fileobj(io.BytesIO(img_bytes), filename)

def get_all_vaccine_img_from_user(id):
    vaccine_list = []
    for bucket_object in bucket.objects.all():
        if bucket_object.key.startswith(id):
            vaccine_list.append(bucket_object.key) 
    return vaccine_list

def download_img_from_s3(filename):
    image = bucket.Object(filename)
    data = image.get().get('Body').read()
    encoed_img = base64.b64encode(data)
    return encoed_img.decode("utf-8")

def filled_vaccine_record_from_image(resident_info, info, doses_number):
    i = resident_info.copy()
    i['id'] = info['id']
    i['name'] = info['name']
    i['phone_number'] = info['phone_number']
    i['email'] = info['email']
    if doses_number == "1":
        i['vaccine_type_1'] = info['vaccine_type_1']
        i['vaccine_date_1'] = info['vaccine_date_1']
    elif doses_number == "2":
        i['vaccine_type_2'] = info['vaccine_type_2']
        i['vaccine_date_2'] = info['vaccine_date_2']
    elif doses_number == "3":
        i['vaccine_type_3'] = info['vaccine_type_3']
        i['vaccine_date_3'] = info['vaccine_date_3']
    return i 

def delete_img_from_s3(filename):
    bucket.delete_objects(Delete={'Objects': [{'Key': filename}]})
def get_image_number(id):
    status_code = dy_ope.get_image_status(id)
    if status_code == "7":
        return status_cannot_upload
    elif status_code != "connection error" or status_code!="Not found":
        status_suffix = status_code_dic[status_code]
        return (status_suffix,status_code)
    else:
        return status_abnormal
def get_image_number_delete(id,suffix):
    status_code = dy_ope.get_image_status(id)
    if status_code != "connection error" or status_code!="Not found":
        #status_suffix = status_code_dic[status_code]
        return (suffix,status_code)
    else:
        return status_abnormal
        
def set_image_status(id,info,add=True):
    if add:
        status_code = status_code_add[info[1]]
        dy_ope.set_image_status_code(id,status_code)
    else:
        status_code = status_code_del[info]
        dy_ope.set_image_status_code(id,status_code)