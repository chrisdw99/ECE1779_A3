from cgi import print_arguments
from crypt import methods
import json
from unittest import result
from flask import render_template, Flask, request, redirect, url_for, flash, session
from app import webapp
#from app import has_file
#rom app import database_operations as db_ope
from app import dynamodb_operations as dy_ope
from app import operations as ope
import app
from app.models import User
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, login_required,logout_user

#admin = False
#has_file = False
@webapp.route('/login',methods=["GET","POST"])
def login():
    session.permanent = True
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method =='POST':
        email = request.form.get('email', "")
        password = request.form.get('password', "")
        user = User.check_login(email,password)
        if user == None:
            message = "Something went wrong with internet connection. Please try again later or contact your administrator."
            return render_template('login.html', message = message)
        elif user == "Not exists":
            message = "User Don't exists, please check and try later or register first."
            return render_template('login.html', message = message)
        elif user == "Wrong Passwd":
            message = "Password wrong, please check again and try later."
            return render_template('login.html', message = message)
        else:
            login_user(user)
            print(f"user admin status {user.admin}")
            print(f"current_user admin status {current_user.is_admin()}")
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
        message = ""
        return render_template('login.html', message = message)
    #    if user=='amy':#
    #     log_success = True
    #     if log_success:
    #         return redirect('/home')
    #     else:
    #         message = "Failed login"
    #         return render_template('login.html', message = message)
    return render_template("login.html")
@webapp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
@webapp.route('/')
@webapp.route('/home',methods=["GET","POST"])
def home():
    return render_template("home.html")
@webapp.route('/residents',methods=['GET'])
@login_required
def residents():
    if current_user.admin:
        print(f"current_user is admin {current_user.admin}")
        query_result = dy_ope.get_all_residents()
        residents = []
        for resident in query_result:
            # item has two columns: image_key, filename(with file extension)
            residents.append([resident["name"],resident["residentID"]])
        return render_template("show_all_residents.html", residents=residents)
    else:
        print(f"current_user is not admin {current_user.admin}")
        query_result = dy_ope.get_one_resident(current_user.id)
        residents= []
        residents.append([query_result["name"],query_result["residentID"]])
        return render_template("show_all_residents.html", residents=residents)
@webapp.route('/add_resident',methods=['GET','POST'])
@login_required
def add_resident():
    if request.method == 'GET':
        #patient_name = request.form.get('patient_name', "")
        #print(patient_name)
        resident_info = ope.init_resident_info(current_user.id)
        # if resident_info == {}:
        #     #current_user.set_file_status(False)
            
        #     print(f"current_user has not set a file {current_user.does_have_file()}")
        # else:
        #     # has_file = True
        #     # current_user.set_file_status(True)
        #     print(f"current_user has set a file {has_file}")
    elif request.method == 'POST':
        patient_name = request.form.get('patient_name', "")
        patient_email = request.form.get('patient_email', "")
        patient_phone = request.form.get('patient_phone', "")
        vaccine_type_1 = request.form.get('vaccine_type_1', "")
        vaccine_time_1 = request.form.get('vaccine_time_1', "")
        vaccine_type_2 = request.form.get('vaccine_type_2', "")
        vaccine_time_2 = request.form.get('vaccine_time_2', "")
        vaccine_type_3 = request.form.get('vaccine_type_3', "")
        vaccine_time_3 = request.form.get('vaccine_time_3', "")
        dose = 0
        #print(patient_name,patient_phone,patient_email)
        resident_info = ope.init_resident_info(current_user.id)
       
        #TODO:save to db
        info = {"id":current_user.id,"name":patient_name, "email":patient_email, "phone_number" :patient_phone,
                "vaccine_type_1":vaccine_type_1,"vaccine_date_1":vaccine_time_1,
                "vaccine_type_2":vaccine_type_2,"vaccine_date_2":vaccine_time_2,
                "vaccine_type_3":vaccine_type_3,"vaccine_date_3":vaccine_time_3,}
#         dose_info = dy_ope.get_resident_doses(current_user.id)
#         if dose_info == "connection error":
#             flash("Internet connection error, please try again later.")
#             return render_template("create_resident.html", resident_info=resident_info)
#         elif dose_info == None:
#             #"The user has no vaccine status file in the system"
#             dy_ope.add_resident(info)
#         else:
#             #"The user already  has  vaccine status file in the system" 
#             dy_ope.update_resident(info)
        # #if has_file:
        #     print(f"Current_user has set a file {has_file}")
        #     result = dy_ope.update_resident(info)
        result = False
        if ope.is_resident_info_completed(info):
            previous_url = request.referrer.rsplit("/")[-1]
            # only process info if the page comes from add_resident_image
            if previous_url == 'add_resident_image':
                doses_number = ope.detect_doses_numner(resident_info, info)
                processed_info = ope.filled_vaccine_record_from_image(resident_info, info, doses_number)
                result= dy_ope.add_resident(processed_info)
            else:
                # else save all the information in the info
                result= dy_ope.add_resident(info)

        # if ope.is_resident_info_completed(info):
        #     print("checkpoint 1")
        #     if 'file' in request.files:
        #         file = request.files['file']
        #         print("checkpoint 2")
        #         dy_ope.add_resident(info)
        #         if file and ope.allowed_file(file.filename):
        #             file_bytes = file.read()
        #             print("checkpoint 3")
        #             if doses_number != "":
        #                 print("checkpoint 4")
        #                 ope.upload_img_to_s3(file_bytes, current_user.id+"-doses-{}".format(doses_number))
        #                 dy_ope.add_resident(info)
        #     else:
        #         print("checkpoint 5")
        #         if session['img_byte'] != '0':
        #             print("checkpoint 6")
        #             # the file is from add_resident_image
        #             file = session['img_byte']
        #             ope.upload_img_to_s3(file, current_user.id+"-doses-{}".format(doses_number))
        #             processed_info = ope.filled_vaccine_record_from_image(resident_info, info, doses_number)
        #             dy_ope.add_resident(processed_info)
        #         else:
        #             print("checkpoint 7")
        #             dy_ope.add_resident(info)
        #     flash("Success.")
        # else:
        #     print("checkpoint 8")
        #     flash("Failed. Please complete the resident's information")
        if result:
            flash("Success")
        else:
            flash("Failed. Please complete the resident's information")

    resident_info = ope.init_resident_info(current_user.id)

    # session['img_byte'] = '0'
    # print(resident_info)
    return render_template("create_resident.html", resident_info=resident_info)

@webapp.route('/add_resident_image',methods=['GET','POST'])
@login_required
def add_resident_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return render_template("create_resident_image.html")
        file = request.files['file']
        if file and ope.allowed_file(file.filename):
            file_bytes = file.read()
            resident = ope.extract_text_as_en(file_bytes)
            if ope.is_resident_info_empty(resident):
                flash("Cannot recognize a resident from the uploaded image")
                render_template("create_resident_image.html")
            else:
                print(resident)
                #session['img_byte'] = file_bytes
                flash("Please check the recognized information and fill in the blanks if any parts are minssing.")
                return render_template("create_resident.html", resident_info=resident)

    return render_template("create_resident_image.html")

@webapp.route('/find_resident',methods=['GET','POST'])
@login_required
def find_resident():
    results = ''
    vaccine_img_list = []
    if request.method == 'GET':
        #name =request.args.get("name")
        id = request.args.get("id")
        if id == None:
            results = []
        else:
            resident = dy_ope.get_one_resident(id)
            results = [resident["name"], resident["email"]]
            if "phone_number" in resident:
                results.append(resident["phone_number"])
            else:
                results.append("")
            if "vaccine_type_1" in resident:
                results.append(resident["vaccine_type_1"])
                results.append(resident["vaccine_date_1"])
            else:
                results.append("")
                results.append("")
            if "vaccine_type_2" in resident:
                results.append(resident["vaccine_type_2"])
                results.append(resident["vaccine_date_2"])
            else:
                results.append("")
                results.append("")
            if "vaccine_type_3" in resident:
                results.append(resident["vaccine_type_3"])
                results.append(resident["vaccine_date_3"])
            else:
                results.append("")
                results.append("")


            vaccine_img_list = []
            vaccine_list = ope.get_all_vaccine_img_from_user(id)
            if len(vaccine_list) != 0:
                for vaccine in vaccine_list:
                    vaccine_img_list.append(ope.download_img_from_s3(vaccine))
    if request.method == 'POST':
        #find in db
        #print(patient_name)
        #results=("amy","123@qq.com","n12345","sinovac","2021","sinovac","2021","sinovac","2022")
        #print(results[0])
        email = request.form.get('email', "")
        user_info = dy_ope.find_user_by_email(email)
        if user_info == None:
            flash("Internet connection error, please try again")
        elif user_info == {}:
            vaccine_img_list = []
            results = []
            flash("No such user.")
        else:
            id = user_info["userid"]
            resident = dy_ope.get_one_resident(id)
            results=[]
            if "name" in resident:
                results.append(resident['name'])
            else:
                results.append("")
            
            if "email" in resident:
                results.append(resident['email'])
            else:
                results.append("")

            if "phone_number" in resident:
                results.append(resident["phone_number"])
            else:
                results.append("")
            if "vaccine_type_1" in resident:
                results.append(resident["vaccine_type_1"])
                results.append(resident["vaccine_date_1"])
            else:
                results.append("")
                results.append("")
            if "vaccine_type_2" in resident:
                results.append(resident["vaccine_type_2"])
                results.append(resident["vaccine_date_2"])
            else:
                results.append("")
                results.append("")
            if "vaccine_type_3" in resident:
                results.append(resident["vaccine_type_3"])
                results.append(resident["vaccine_date_3"])
            else:
                results.append("")
                results.append("")


            vaccine_img_list = []
            vaccine_list = ope.get_all_vaccine_img_from_user(id)
            if len(vaccine_list) != 0:
                for vaccine in vaccine_list:
                    vaccine_img_list.append(ope.download_img_from_s3(vaccine))
    return render_template("search_resident.html", results=results, images=vaccine_img_list)
@webapp.route('/register',methods=["GET","POST"])
def register():
    if request.method == 'POST':
        info = {}
        info["email"] =request.form.get('email')
        info["password"] = request.form.get('password')
        result = dy_ope.register(info)
        if result == True:
            message = "Register success!"
            return render_template("register.html", message=message)
        elif result == "User Exists":
            message = "User Exists! Please login in directly"
            return render_template("register.html", message=message)
        elif result == "Internet Connection Error":
            message="Internet Connection Error"
            return render_template("register.html", message=message)
        else:
            message="Register failed! Please try again later."
            return render_template("register.html", message=message)
    return render_template("register.html")

@webapp.route('/db_changed',methods=["GET","POST"])
def db_changed():
    flash("DB has changed, please refresh the page to get latest data.")
    return webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json'
    )
@webapp.route('/show_personal',methods=['GET','POST'])
@login_required
def show_personal():
    results = ''
    vaccine_list = []
        #name =request.args.get("name")
    id = None

    if current_user.admin:
        id  = request.args.get("id")
    else:
        id = current_user.id

    if id == None:
        results = []
    else:
        resident = dy_ope.get_one_resident(id)

        results=[]
        if "name" in resident:
            results.append(resident['name'])
        else:
            results.append("")

        if "email" in resident:
            results.append(resident['email'])
        else:
            results.append("")

        if "phone_number" in resident:
            results.append(resident["phone_number"])
        else:
            results.append("")
        if "vaccine_type_1" in resident:
            results.append(resident["vaccine_type_1"])
            results.append(resident["vaccine_date_1"])
        else:
            results.append("")
            results.append("")
        if "vaccine_type_2" in resident:
            results.append(resident["vaccine_type_2"])
            results.append(resident["vaccine_date_2"])
        else:
            results.append("")
            results.append("")
        if "vaccine_type_3" in resident:
            results.append(resident["vaccine_type_3"])
            results.append(resident["vaccine_date_3"])
        else:
            results.append("")
            results.append("")


        vaccine_img_list = []
        vaccine_name_list = ope.get_all_vaccine_img_from_user(id)
        if len(vaccine_name_list) != 0:
            for vaccine in vaccine_name_list:
                vaccine_img_list.append(ope.download_img_from_s3(vaccine))
        vaccine_list = list(zip(vaccine_name_list, vaccine_img_list))
        #find in db
        #print(patient_name)
        #results=("amy","123@qq.com","n12345","sinovac","2021","sinovac","2021","sinovac","2022")
        #print(results[0])
    return render_template("show_personal_info.html", results=results, vaccine_list=vaccine_list, id=id)

@webapp.route('/change_password',methods=['GET','POST'])
@login_required
def change_password():
    if request.method == 'POST':
        id = current_user.id
        old_password = request.form.get('old_password', "")
        new_password = request.form.get('new_password', "")
        verify_password = request.form.get('verify_password', "")
        if verify_password!=new_password:
            flash("The new passwords don't match with each other!")
        else:
            if User.check_password_only(id,old_password):
                result = User.update_password(id,new_password)
                if result:
                    flash("The new password has been set.")
                    return redirect(url_for('logout'))
                else:
                    flash("Internet connection error. Please check and try again.")
            else:
                flash("The original password is not correct!")
    return render_template("change_password.html")

@webapp.route('/add_vaccine_receipt', methods=['GET', 'POST'])
@login_required
def add_vaccine_receipt():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
        file = request.files['file']
        if file and ope.allowed_file(file.filename):
            file_bytes = file.read()
            id = current_user.id
            image_number = ope.get_image_number(id)
            if image_number == ope.status_cannot_upload:
                flash("Failed. The user cannot upload more images.")
            elif image_number != ope.status_abnormal:
                filename = id+"-{}".format(image_number[0])
                ope.upload_img_to_s3(file_bytes, filename)
                ope.set_image_status(id, image_number, True)
                flash("Successfully upload the vaccine certificate")
            else:
                flash("Failed")
        else:
            flash("Failed")
    return render_template("add_vaccine_receipt.html")

@webapp.route('/personal_change_image/<string:image_name>/<string:id>', methods=['POST'])
def personal_change_image(image_name, id):
    if 'file' not in request.files:
        flash('No file part')
    file = request.files['file']
    if file and ope.allowed_file(file.filename):
        file_bytes = file.read()
        ope.upload_img_to_s3(file_bytes, image_name)
        flash("Successfully change image")
    
    return redirect(url_for('show_personal', id=id))

@webapp.route('/personal_delete_image/<string:image_name>/<string:id>', methods=['POST'])
@login_required
def personal_delete_image(image_name, id):
    #image_number = ope.get_image_number(id)
    #Get the suffix from the image_name
    suffix = image_name.rsplit("-")[-1]
    image_status = ope.get_image_number_delete(id,suffix)
    if image_status != ope.status_abnormal:
        ope.set_image_status(id, image_status, False)
        ope.delete_img_from_s3(image_name)
        flash('Successfully delete image')
    else:
        flash("Failed")
    return redirect(url_for('show_personal', id=id))

@webapp.route('/delete_resident/<string:id>', methods=['POST'])
@login_required
def delete_resident(id):
    vaccine_name_list = ope.get_all_vaccine_img_from_user(id)
    for vaccine in vaccine_name_list:
        ope.delete_img_from_s3(vaccine)
    dy_ope.delete_resident(id)
    return redirect(url_for('residents'))