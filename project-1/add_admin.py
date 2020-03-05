import re
import re
from time import strftime
from flask import jsonify
import math, random
import requests
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from geopy.exc import GeocoderTimedOut
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from flask_login import login_user, logout_user, login_required, LoginManager
from flask import Flask, render_template, url_for, request, redirect, jsonify, json, session, flash
from pymongo import MongoClient
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from time import strftime
import re, os
import random
import string
from pptx.compat import Unicode
import smtplib
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from geopy.geocoders import Nominatim

app = Flask(__name__)
CORS(app)
# UPLOAD_FOLDER = "/var/www/html/smartbike"
# ALLOWED_EXTENSIONS = set(['mp4', 'mov','wmv', 'flv', 'avi'])
# FILE_ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc','docx'])

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = "/var/www/html/smart_bike"
ALLOWED_EXTENSIONS = set(['mp4', 'mov', 'wmv', 'flv', 'avi'])
FILE_ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc', 'docx'])

app = Flask(__name__)
app.config["MONGO_DBNAME"] = "smart_bike"
app.config['MONGO_URI'] = 'mongodb://35.154.239.192:6909/smart_bike'
mongo = PyMongo(app)
CORS(app)

client = MongoClient('35.154.239.192:6909')
# client = MongoClient('localhost')


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'indiral@fugenx.com'
app.config['MAIL_PASSWORD'] = 'fugenx@231456'
app.config['MAIL_DEFAULT_SENDER'] = 'default_sender_email'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['DEBUG'] = True
app.secret_key = 'my secret key'
app.config['MAIL_ASCII_ATTACHMENTS'] = True
app.config['SESSION_USE_SIGNER'] = True

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

s = URLSafeTimedSerializer('12345')
login_manager = LoginManager()
login_manager.init_app(app)
mail = Mail(app)

CORS(app)
UPLOAD = os.path.join(APP_ROOT, 'Images')
if not os.path.exists(UPLOAD):
    os.makedirs(UPLOAD, exist_ok=True)
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD = os.path.join(APP_ROOT, 'Files')
if not os.path.exists(UPLOAD):
    os.makedirs(UPLOAD, exist_ok=True)
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/smartbike/superadmin/login', methods=['POST', 'GET'])
def super_admin():
    try:
        data = client.smartbike_admin
        coll = data.smartbike_admin_user
        output = []
        email_id = request.json['email_id']
        password = request.json['password']
        roles_id = int(1)
        if email_id == "superadmin@gmail.com" and password == "admin@123" and roles_id == 1:
            coll.insert({'email_id': email_id, 'Password': password, 'roles_id': 1})
            output.append({'email_id': email_id, 'Password': password, 'roles_id': 1})
            return jsonify({'result': 'registered success', 'output': output})
        else:
            return jsonify({'result': 'password credentials fail'})
    except Exception as e:
        return jsonify(status="successfully registered", message=str(e))

# ###############################login based on role id##########################
# @app.route('/smartbike/superadmin/login', methods=['POST', 'GET'])
# def super_admin():
#     try:
#         data = client.smartbike_admin
#         coll = data.smartbike_admin_user
#         email_id = request.json['email_id']
#         password = request.json['password']
#         details  = coll.find


###################################################################
def randomStringDigits(stringLength=4):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))
#################################admin_user_add##################################
@app.route('/smart_bike/admin_user', methods=['POST'])
def register():
    data = client.smartbike_admin
    coll = data.smartbike_admin_users
    output = []
    try:
        user_name = request.json['user_name']
        try:
            email_id = request.json['email_id']
        except KeyError:
            email_id = ""

        mobile_number = request.json['mobile_number']
        password = randomStringDigits(6)
        print(password)
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        created_time = strftime("%Y/%m/%d %H:%M:%S %I%p")
        Role = request.json['Role']
        Roles_id = int(2)
        #
        # Role_list = [j['Role_id'] for j in coll.find()]
        # if len(Role_list) is 0:
        #     Role_id = 1
        # else:
        #     Role_id = int(Role_list[-1]) + 1


        # url = "https://api.msg91.com/api/sendhttp.php?mobiles=" + mobile_number + "&authkey=293844AlhYRFCo5d7b2d94&route=4&sender=SMTBYK&message=Your PASSWORD IS" + ' ' + str(
        #     password) + "&country=91"
        msg = Message('your smart bike account password is', sender="indiral@fugenx.com", recipients=[email_id])
        msg.body = 'Thank you for registering with us.\n\n\n. Please use %s \n\n\n Thankyou\n' % password
        mail.send(msg)
        # f = requests.get(url)

        user_id_list = [i['user_id'] for i in coll.find()]
        if len(user_id_list) is 0:
            user_id = 1
        else:
            user_id = int(user_id_list[-1]) + 1

        er = coll.find({'email_id': email_id})
        mr = coll.find({'mobile_number': mobile_number})
        for m in mr:
            if m['mobile_number'] == mobile_number:
                return jsonify({'status': 'failure',
                                'message': 'Seems like you have already registered wth us.Please login to continue.'})
        #
        # if re.match(pattern=r'(^(0/91))?([0-9]{10}$)', string=mobile_number):  # check for mobilenumber properly
        #
        #     # output = []

            # Role = ['Limited_Access', 'Full_Access ']
        if (Role == 'Limited_Access'):

                coll.insert(
                    {'user_name': user_name, 'email_id': email_id,
                     'user_id': user_id, 'first_name': first_name, 'last_name': last_name,
                     'Role': 'Limited_Access', 'password': password,
                     'mobile_number': mobile_number, 'Roles_id': 2, 'created_time': created_time})
                output.append(
                    {'user_name': user_name, 'email_id': email_id, 'first_name': first_name, 'last_name': last_name,
                     'user_id': user_id, 'Role': 'Limited_Access', 'password':password,
                     'mobile_number': mobile_number, 'Roles_id': 2, 'created_time': created_time})
                return jsonify({'status': 'success', 'message': 'you r in limited access', 'result': output})
            # return jsonify({'status': 'success', 'message': 'you r in limited access', 'result': output})

        elif (Role == 'Full_Access'):
                coll.insert(
                    {'user_name': user_name, 'email_id': email_id, 'first_name': first_name, 'last_name': last_name,
                     'user_id': user_id, 'Role': 'Full_Access', 'password': password,
                     'mobile_number': mobile_number, 'created_time': created_time, 'Roles_id': 2})
                output.append(
                    {'user_name': user_name, 'email_id': email_id, 'first_name': first_name, 'last_name': last_name,
                     'user_id': user_id, 'password': password,
                     'Role': 'Full_Access', 'mobile_number': mobile_number, 'created_time': created_time,
                     'Roles_id': 2})
                return jsonify({'status': 'success', 'message': 'you r in full access', 'result': output})
        else:
            return jsonify({'status':'fail'})
        #
        #
        # else:
        #         return jsonify({'status': 'failure', 'message': 'Invalid Mobile Number'})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))


##################################admin_user_ delete################################
@app.route('/smart_bike/delete_admin', methods=['POST', 'GET'])
def delete_admin():
    try:
        data = client.smartbike_admin
        coll = data.smartbike_admin_users
        user_id = request.json['user_id']

        for q in coll.find({'user_id': user_id}):
            coll.remove({'user_id': user_id})

        return jsonify({'status': 'delete admin successfully'})

    except Exception as e:
        return jsonify(status="fail", message=str(e))


##############################admin-details###########################
@app.route('/smart_bike/admin_details', methods=['POST', 'GET'])
def admin_details():
    try:
        data = client.smartbike_admin
        coll = data.smartbike_admin_users
        user_id = request.json['user_id']
        details = coll.find()
        output = []
        for i in details:
            print(i)
            id = i['user_id']
            print(id)
            if int(user_id) == int(id):
                output.append({'username': i['user_name'], 'email_id': i['email_id'], 'first_name': i['first_name'],
                               'mobile_number': i['mobile_number'], 'created_time': i['created_time']})
                return jsonify({'status': 'True', 'message': 'ok', 'result': output})
        return jsonify({'status': 'True'})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))


######################################role_management###########################################
#################################################add_role_management######################
@app.route('/smart_bike/add_role_admin/<user_id>', methods=['GET', 'POST'])
def role(user_id):
    try:
        data = client.smartbike_admin
        coll = data.smartbike_admin_users
        # data = client.smartbike_admin
        # coll = data.smartbike_rolemanagement
        role_name = request.json['role_name']
        created_time = strftime("%Y/%m/%d %H:%M:%S %I%p")

        output = []

        # user_id = request.json['user_id']
        # for q in coll.find():
        # if user_id == int(user_id):
        coll.update({'user_id': int(user_id)}, {'$set': {'role_name': role_name, 'created_time': created_time}})
        output.append({'role_name': role_name, 'created_time': created_time})

        return jsonify({'staus': 'success', 'message': 'access', 'result': output})

    except Exception as e:
        return jsonify(status="Fail", message=str(e))




###############################edit_admin#################################
@app.route('/smart_bike/edit_admin', methods=['POST'])
def my_profile_update():
    data = client.smartbike_admin
    coll = data.smartbike_admin_users
    output = []
    try:
        user_id = request.json['user_id']
        email_id = request.json['email_id']
        last_name = request.json['last_name']
        first_name = request.json['first_name']
        mobile_number = request.json['mobile_number']
        role_name = request.json['role_name']
        confirm_role_name = request.json['confirm_role_name']
        if role_name != confirm_role_name:
            return "Passwords do not match. try again"

        # updated_time = strftime("%Y/%m/%d %H:%M:%S %I%p")
        coll.update({'user_id': user_id},
                    {'$set': {'first_name': first_name, 'last_name': last_name, 'email_id': email_id,
                              'mobile_number': mobile_number, 'role_name': role_name,
                              'confirm_role_name': confirm_role_name}})
        # output = []
        # details = coll.find()
        # for j in details:
        output.append({'user_id': user_id, 'first_name': first_name, 'last_name': last_name, 'email_id': email_id,
                       'role_name': role_name, 'confirm_role_name': confirm_role_name,
                       'mobile_number': mobile_number})
        return jsonify({'status': 'success', 'message': 'Profile updated successfully', 'result': output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))


@app.route('/smart_bike/get_admin_user_info', methods=['GET'])
def get_details1():
    try:
        data = client.smartbike_admin
        coll = data.smartbike_admin_users
        output = []
        for q in coll.find():
            output.append({'user_id': q['user_id'], 'user_name': q['user_name'], 'first_name': q['first_name'],
                           'last_name': q['last_name'],
                           'mobile_number': q['mobile_number'], 'email_id': q['email_id'], 'Role': q['Role']})
        return jsonify({'status': 'success', 'message': 'all  details get successfully', "result": output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

######################get_user_infouser_id################
@app.route('/smart_bike/get_admin_user_edit_info/<user_id>', methods=['GET'])
def edit_get_details1(user_id):
    try:
        data = client.smartbike_admin
        coll = data.smartbike_admin_users
        output = []
        for q in coll.find():
            id = q['user_id']
            if id == int(user_id):
               output.append({'user_id': q['user_id'], 'user_name': q['user_name'], 'first_name': q['first_name'],
                           'last_name': q['last_name'],
                           'mobile_number': q['mobile_number'], 'email_id': q['email_id'], 'Role': q['Role']})
               return jsonify({'status': 'success', 'message': 'get admin by id success', "result": output})
        else:
            return jsonify({'status':'fail'})

    except Exception as e:
        return jsonify(status="Fail", message=str(e))



############################################kyc_management##############################

##########################getting the details of user through registration################
@app.route('/smart_bike/get_user_info/<user_id>', methods=['POST', 'GET'])
def get_user_info(user_id):
    db = client.smart_bike
    coll = db.smart_bike_users
    output = []
    # user_id= request.json['user_id']
    info = coll.find()
    for i in info:
        user = i['user_id']   # i is for iterating the no.of users in database
        ks = i['kyc_status']
        print(ks)
        if user == int(user_id):
            user_name = i['user_name']
            mobile_number = i['mobile_number']
            email_id = i['email_id']
            first_name = i['first_name']
            last_name = i['last_name']
            date_of_upload = i['date_of_upload']
            date_of_verified = i['date_of_verified']
            try:
                upload_pic = i['upload_img_path']
                # kyc_status: i['kyc_status']
            except KeyError or ValueError:
                upload_pic = ""
            output.append(
                {'user_id': user, 'user_name': user_name, 'mobile_number': mobile_number, 'email_id': email_id,
                 'first_name': first_name, 'last_name': last_name, 'date_of_upload': date_of_upload,
                 'kyc_status': i['kyc_status'], 'date_of_verified': date_of_verified, 'upload_pic': upload_pic})
            return jsonify({'status': 'success', 'result': output})
    else:
        return jsonify({'status': 'fail', 'result': 'Unable to retrieve user details, Please try again'})


#################################### edit-kyc #########################################

@app.route('/smart_bike/kyc_edit', methods=['POST'])
def KYC_update():
    # data = client.smartbike_admin
    # coll = data.smartbike_admin_u
    # ser
    db = client.smart_bike
    coll = db.smart_bike_users
    output = []
    try:
        user_id = request.json['user_id']
        email_id = request.json['email_id']
        last_name = request.json['last_name']
        first_name = request.json['first_name']
        mobile_number = request.json['mobile_number']

        info = coll.find()
        for i in info:
            user_id = i['user_id']
            kyc_status = i['kyc_status']
            id_proof = i['id_proof']
            if user_id == int(user_id):
                coll.update({'user_id': user_id}, {
                    '$set': {'first_name': first_name, 'last_name': last_name, 'email_id': email_id,
                             'kyc_status': kyc_status, 'id_proof': id_proof,
                             'mobile_number': mobile_number, }})

                output.append(
                    {'user_id': user_id, 'first_name': first_name, 'last_name': last_name, 'email_id': email_id,
                     'kyc_status': kyc_status, 'id_proof': id_proof,
                     'mobile_number': mobile_number})
                return jsonify({'status': 'success', 'message': 'Profile updated successfully', 'result': output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))


###############################role-based authentication#############################
@app.route('/smart_bike/admin/login/', methods=['POST', 'GET'])
def admins_login():
    # try:
    data = client.smartbike_admin
    coll = data.smartbike_admin_user
    coll1 = data.smartbike_admin_users
    email_id = request.json['email_id']
    password = request.json['password']

    details = coll.find()
    details1 = coll1.find()
    output = []
    for i in details:
        id = i['email_id']
        pwd = i['Password']
        role_id = i['roles_id']
        print(id)
        print(pwd)
        for j in details1:
            id1 = j['email_id']
            pwd1 = j['password']
            role_id1 = j['Roles_id']
            print(id1)
            print(pwd1)
            print(role_id1)

            if str(email_id) == str(id) and str(password) == str(pwd) and int(role_id) == 1:
                output.append({'email_id': i['email_id'], 'password': i['Password']})
                print(output)
                return jsonify({'status': 'True', 'message': 'login successful', 'result': output})
            elif str(email_id) == str(id1) and str(password) == str(pwd1) and int(role_id1) == 2:
                output.append({'email_id': j['email_id'], 'password': j['password']})
                print(output)
                return jsonify({'status': 'True', 'message': 'login successful', 'result': output})

    return jsonify({'status': 'False', 'message': 'wrong login credentials'})


##################################get-customer-details####################################
@app.route('/smart_bike/customer_details', methods=['GET'])
def customer_details():
    db = client.smart_bike
    coll = db.smart_bike_users
    output_list = []
    details = coll.find()
    for j in details:
        temp_dict = {}
        temp_dict['user_id'] = j['user_id']
        temp_dict['user_name'] = j['user_name']
        temp_dict['first_name'] = j['first_name']
        temp_dict['last_name'] = j['last_name']
        temp_dict['mobile_number'] = j['mobile_number']
        temp_dict['email_id'] = j['email_id']
        temp_dict['kyc_status'] = j['kyc_status']
        try:
            temp_dict['login_type'] = j['login_type']
        except KeyError or ValueError:
            temp_dict['login_type'] = ""

        output_list.append(temp_dict)
    return jsonify({"status": "success", "message": "List of Profile", "result": output_list})


##################################bike-details-management#####################################
@app.route('/smart_bike/upload_bike_details', methods=['POST'])
def bike_details():

        data = client.smartbike_admin
        coll = data.bike_details
        city_id = int(request.json['city_id'])
        city_name = request.json['city_name']
        state_id = int(request.json['state_id'])
        state_name = request.json['state_name']
        station_number =int(request.json['station_number'])
        station_name = request.json['station_name']
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        country = request.json['country']
        bike_type = request.json['bike_type']
        bike_make = request.json['bike_make']
        bike_frame_number = int(request.json['bike_frame_number'])
        bike_lock_number = int(request.json['bike_lock_number'])
        bike_lock_type = request.json['bike_lock_type']
        bike_color = request.json['bike_color']
        bike_mode = request.json['bike_mode']
        published_on = strftime("%Y/%m/%d %H:%M:%S %I%p")

        Available_ride_date = request.json['Available_ride_date']
        date_of_purchase = request.json['date_of_purchase']
        bike_id_list = [i['bike_id'] for i in coll.find()]
        if len(bike_id_list) is 0:
            bike_id = 1
        else:
            bike_id = int(bike_id_list[-1]) + 1
        output = []

        coll.insert(
                    {'bike_id': bike_id, 'city_name': city_name, city_id:int(city_id), 'state_id': int(state_id),
                     'state_name': state_name,
                     'station_number':int(station_number), 'station_name': station_name, 'bike_type': bike_type, 'bike_make': bike_make,
                     'bike_frame_number': bike_frame_number, 'bike_lock_number': bike_lock_number,'latitude':latitude,'longitude':longitude,
                     'bike_lock_type': bike_lock_type,
                     'bike_mode': bike_mode, 'bike_color': bike_color, 'country':country,'published_on': published_on,
                     'published_status': 'published', 'Available_ride_date': Available_ride_date,
                     'date_of_purchase': date_of_purchase})
        output.append(
                    {'bike_id': bike_id, 'city_name': city_name, 'city_id':city_id, 'state_id':int(state_id),
                     'state_name': state_name,
                     'station_number': station_number, 'station_name': station_name, 'bike_type': bike_type, 'bike_make': bike_make,
                     'bike_frame_number': bike_frame_number, 'bike_lock_number': bike_lock_number,
                     'bike_lock_type': bike_lock_type,'latitude':latitude,'longitude':longitude,
                     'bike_mode': bike_mode, 'bike_color': bike_color, 'published_on': published_on,
                     'published_status': 'published', 'Available_ride_date': Available_ride_date,
                     'date_of_purchase': date_of_purchase})
        print(output)
        return jsonify({'status': "success", 'message': "uploaded successfully", 'result': output})


# ###############################images and files##########################################################
# @app.route('/smart_bike/file_upload/<bike_frame_number>', methods=['POST'])
# def upload_file(bike_frame_number):
#     db = client.smartbike_admin
#     coll = db.bike_details
#     # bike_id = request.form['bike_id']
#     st = random.randint(1000, 9999)
#     output = []
#     upload_documents = []
#     image_path1 = []
#     upload_bike_images = []
#     image_path = []
#     # qrcode_image=[]
#     if request.method == 'POST' and 'images' in request.files:
#         for f in request.files.getlist('images'):
#             # print(request.files.getlist)
#             os.makedirs(os.path.join(UPLOAD_FOLDER), exist_ok=True)
#             filename = secure_filename(f.filename)
#             upload_bike_images.append(filename)
#             # print(upload_image)
#             mongo_db_path = "/Images/"+ filename + str(st)
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             image_path.append(mongo_db_path)
#             f.save(filepath)
#     if request.method == 'POST' and 'files' in request.files:
#         for i in request.files.getlist('files'):
#             # print(request.files.getlist)
#             os.makedirs(os.path.join(UPLOAD_FOLDER), exist_ok=True)
#             filename = secure_filename(i.filename)
#             upload_documents.append(filename)
#             # print(upload_image)
#             mongo_db_path1 = "/Files/" + filename + str(st)
#             filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             image_path1.append(mongo_db_path1)
#             i.save(filepath1)
#         details = coll.find_one_and_update({'bike_frame_number': int(bike_frame_number)}, {
#                 '$set': {'upload_bike_images': image_path, 'upload_documents': image_path1}})
#         print(details)
#
#         output.append({'upload_bike_images': image_path, 'upload_documents': image_path1})
#         return jsonify({'status': 'True', 'message': 'uploaded successfully', 'result': output})
#     else:
#             return jsonify({'status': 'False', 'message': 'failed to upload'})
#
#
#


# @app.route('/smart_bike/upload_bike_details', methods=['POST'])
# def bike_details():
#     data = client.smartbike_admin
#     coll = data.bike_details
#     # state_id = (int)(request.form['state_id'])
#     state_name = request.form['state_name']
#     country = request.form['country']
#     # city_id = (int)(request.form['city_id'])
#     city_name = request.form['city_name']
#     station_number = (int(request.form['station_number']))
#     # station_name = request.form['station_name']
#     # latitude = request.form['latitude']
#     # longitude = request.form['longitude']
#     bike_type = request.form['bike_type']
#     bike_make = request.form['bike_make']
#     # total_no_of_bikes=(int(request.form['total_no_of_bikes']))
#     bike_frame_number = (int(request.form['bike_frame_number']))
#     bike_lock_number = (int(request.form['bike_lock_number']))
#     bike_lock_type = request.form['bike_lock_type']
#     bike_color = request.form['bike_color']
#     bike_mode = request.form['bike_mode']
#     published_on = strftime("%Y/%m/%d %H:%M:%S %I%p")
#     published_status = True
#     Available_ride_date = request.form['Available_ride_date']
#     date_of_purchase = request.form['date_of_purchase']
#     bike_id_list = [i['bike_id'] for i in coll.find()]
#     if len(bike_id_list) is 0:
#         bike_id = 1
#     else:
#         bike_id = int(bike_id_list[-1]) + 1
#     # output = []
#     output = []
#     upload_documents = []
#     image_path1 = []
#     upload_bike_images = []
#     image_path = []
#     if request.method == 'POST' and 'images' in request.files:
#         for f in request.files.getlist('images'):
#             # print(request.files.getlist)
#             os.makedirs(os.path.join(UPLOAD_FOLDER), exist_ok=True)
#             filename = secure_filename(f.filename)
#             upload_bike_images.append(filename)
#             # print(upload_image)
#             mongo_db_path = "/Images/" + filename
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             image_path.append(mongo_db_path)
#             f.save(filepath)
#     if request.method == 'POST' and 'files' in request.files:
#         for i in request.files.getlist('files'):
#             # print(request.files.getlist)
#             os.makedirs(os.path.join(UPLOAD_FOLDER), exist_ok=True)
#             filename = secure_filename(i.filename)
#             upload_documents.append(filename)
#             # print(upload_image)
#             mongo_db_path1 = "/Files/" + filename
#             filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             image_path1.append(mongo_db_path1)
#             i.save(filepath1)
#     coll1 = data.smartbike_places
#     details = coll1.find({'station_number': station_number})
#     for i in details:
#         station_number = i['station_number']
#         station_name = i['station_name']
#         latitude = i['latitude']
#         longitude = i['longitude']
#         city_id = i['city_id']
#         state_id = i['state_id']
#         bike_racks = i['bike_racks']
#         total_no_of_bikes=i['total_no_of_bikes']
#
#         coll.insert(
#             {'bike_id': bike_id, 'city_name': city_name, 'city_id': city_id, 'state_id': state_id,
#              'state_name': state_name,
#              'station_number': station_number, 'station_name': station_name, 'latitude': latitude,
#              'longitude': longitude, 'country': country, 'bike_type': bike_type, 'bike_make': bike_make,
#              'bike_frame_number': bike_frame_number, 'bike_lock_number': bike_lock_number,'total_no_of_bikes':total_no_of_bikes,
#              'upload_bike_images': image_path, 'upload_documents': image_path1,
#              'bike_lock_type': bike_lock_type, 'bike_racks': bike_racks,
#              'bike_mode': bike_mode, 'bike_color': bike_color, 'published_on': published_on,
#              'published_status': 'published', 'Available_ride_date': Available_ride_date,
#              'date_of_purchase': date_of_purchase})
#         output.append(
#             {'bike_id': bike_id, 'city_name': city_name, 'city_id': city_id, 'state_id': state_id,
#              'state_name': state_name,
#              'station_number': station_number, 'station_name': station_name, 'latitude': latitude,
#              'longitude': longitude, 'country': country, 'bike_type': bike_type, 'bike_make': bike_make,
#              'bike_frame_number': bike_frame_number, 'bike_lock_number': bike_lock_number,'total_no_of_bikes':total_no_of_bikes,
#              'upload_bike_images': image_path, 'upload_documents': image_path1,
#              'bike_lock_type': bike_lock_type,
#              'bike_mode': bike_mode, 'bike_color': bike_color, 'published_on': published_on,
#              'published_status': 'published', 'Available_ride_date': Available_ride_date,
#              'date_of_purchase': date_of_purchase})
#         return jsonify({'status': "success", 'message': "uploaded successfully", 'result': output})
#
#
# ###############################images and files##########################################################
# @app.route('/smart_bike/file_upload/', methods=['POST'])
# def upload_file():
#     db = client.smartbike_admin
#     coll = db.bike_details
#     bike_frame_number = request.form['bike_frame_number']
#     output = []
#     upload_documents = []
#     image_path1 = []
#     upload_bike_images = []
#     image_path = []
#     if request.method == 'POST' and 'images' in request.files:
#         for f in request.files.getlist('images'):
#             # print(request.files.getlist)
#             os.makedirs(os.path.join(UPLOAD_FOLDER), exist_ok=True)
#             filename = secure_filename(f.filename)
#             upload_bike_images.append(filename)
#             # print(upload_image)
#             mongo_db_path = "/Images/" + filename
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             image_path.append(mongo_db_path)
#             f.save(filepath)
#     if request.method == 'POST' and 'files' in request.files:
#         for i in request.files.getlist('files'):
#             # print(request.files.getlist)
#             os.makedirs(os.path.join(UPLOAD_FOLDER), exist_ok=True)
#             filename = secure_filename(i.filename)
#             upload_documents.append(filename)
#             # print(upload_image)
#             mongo_db_path1 = "/Files/" + filename
#             filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             image_path1.append(mongo_db_path1)
#             i.save(filepath1)
#         details = coll.insert({'bike_frame_numebr': bike_frame_number},
#                               {'$set': {'upload_bike_images': image_path, 'upload_documents': image_path1}})
#         print(details)
#
#         output.append({'upload_bike_images': image_path, 'upload_documents': image_path1})
#         return jsonify({'status': 'True', 'message': 'uploaded successfully', 'result': output})
#     else:
#         return jsonify({'status': 'False', 'message': 'failed to upload'})

#
# ###########################################deleting bike-details#######################
# @app.route('/smart_bike/delete_bike', methods=['POST', 'GET'])
# def delete_bike():
#     try:
#         db = client.smartbike_admin
#         coll = db.smartbike_bike_details
#         bike_id = request.json['bike_id']
#
#         for q in coll.find({'bike_id': bike_id}):
#             coll.remove({'bike_id': bike_id})
#
#         return jsonify({'status': 'delete admin successfully'})
#
#     except Exception as e:
#         return jsonify(status="fail", message=str(e))


############################################### get-bike-details ######################
@app.route('/smart_bike/get_bike_details', methods=['GET'])
def get_bike_details():
    db = client.smartbike_admin
    coll = db.smartbike_bike_details
    data = coll.find()
    output_list = []
    for j in data:
        temp_dict = {}
        try:
            temp_dict['bike_id'] = j['bike_id']
        except KeyError or ValueError:
            temp_dict['bike_id'] = ""
        try:
            temp_dict['city_name'] = j['city_name']
        except KeyError or ValueError:
            temp_dict['city_name'] = ""
        try:
            temp_dict['city_id'] = j['city_id']
        except KeyError or ValueError:
            temp_dict['city_id'] = ""
        try:
            temp_dict['state_name'] = j['state_name']
        except KeyError or ValueError:
            temp_dict['state_name'] = ""
        try:
            temp_dict['state_id'] = j['state_id']
        except KeyError or ValueError:
            temp_dict['state_id'] = ""
        try:
            temp_dict['station_name'] = j['station_name']
        except KeyError or ValueError:
            temp_dict['station_name'] = ""
        try:
            temp_dict['station_number'] = j['station_number']
        except KeyError or ValueError:
            temp_dict['station_id'] = ""
        try:
            temp_dict['bike_type'] = j['bike_type']
        except KeyError or ValueError:
            temp_dict['bike_type'] = ""
        try:
            temp_dict['bike_frame_number'] = j['bike_frame_number']
        except KeyError or ValueError:
            temp_dict['bike_frame_number'] = ""
        try:
            temp_dict['bike_make'] = j['bike_make']
        except KeyError:
            temp_dict['bike_make'] = ""
        try:
            temp_dict['bike_lock_number'] = j['bike_lock_number']
        except KeyError or ValueError:
            temp_dict['bike_lock_number'] = ""
        try:
            temp_dict['bike_lock_type'] = j['bike_lock_type']
        except KeyError or ValueError:
            temp_dict['bike_lock_type'] = ""
        try:
            temp_dict['bike_lock_status'] = j['bike_lock_status']
        except KeyError or ValueError:
            temp_dict['bike_lock_status'] = ""
        try:
            temp_dict['bike_mode'] = j['bike_mode']
        except KeyError or ValueError:
            temp_dict['bike_mode'] = ""
        try:
            temp_dict['bike_color'] = j['bike_color']
        except KeyError or ValueError:
            temp_dict['bike_color'] = ""
        try:
            temp_dict['published_status'] = j['published_status']
        except KeyError or ValueError:
            temp_dict['published_status'] = ""
        try:
            temp_dict['published_on'] = j['published_on']
        except KeyError or ValueError:
            temp_dict['published_on'] = ""
        try:
            temp_dict['upload_bike_images'] = j['upload_bike_images']
        except KeyError or ValueError:
            temp_dict['upload_bike_images'] = ""
        try:
            temp_dict['upload_documents'] = j['upload_documents']
        except KeyError or ValueError:
            temp_dict['upload_documents'] = ""
        try:
            temp_dict['Available_ride_date'] = j['Available_ride_date']
        except KeyError or ValueError:
            temp_dict['Available_ride_date'] = ""
        try:
            temp_dict['total_no_of_bikes'] = j['total_no_of_bikes']
        except KeyError or ValueError:
            temp_dict['total_no_of_bikes'] = ""
        try:
            temp_dict['date_of_purchase'] = j['date_of_purchase']
        except KeyError or ValueError:
            temp_dict['date_of_purchase'] = ""
        output_list.append(temp_dict)
    return jsonify({"status": "success", "message": "List of Profile", "result": output_list})



##################################customer_ delete###############################
@app.route('/smart_bike/customer_delete', methods=['POST', 'GET'])
def customer_delete():
    try:
        db = client.smart_bike
        coll = db.smart_bike_users
        user_id = request.json['user_id']

        for q in coll.find({'user_id': user_id}):
            coll.remove({'user_id': user_id})

        return jsonify({'status': 'delete  successfully'})

    except Exception as e:
        return jsonify(status="fail", message=str(e))


##################################parking-management####################################
@app.route('/smart_bike/parking_bike_details', methods=['POST'])
def parking_details():
    data = client.smartbike_admin
    coll = data.bike_parking_details

    city_id = int(request.json['city_id'])
    city_name = request.json['city_name']
    state_id = int(request.json['state_id'])
    state_name = request.json['state_name']
    station_number = request.json['station_number']
    parking_station_name = request.json['parking_station_name']
    bike_type = request.json['bike_type']
    zone_area = request.json['zone_area']
    # published = strftime("%Y/%m/%d %H:%M:%S %I%p")
    published_on = strftime('%Y-%m-%d')
    # date_of_purchase = strftime('%Y-%m-%d')
    status = []

    parking_id_list = [i['parking_id'] for i in coll.find()]
    if len(parking_id_list) is 0:
        parking_id = 1
    else:
        parking_id = int(parking_id_list[-1]) + 1
    output = []
    # if status== True:
    coll.insert({'parking_id': parking_id, 'city_name': city_name, 'city_id': city_id, 'state_id': state_id,
                 'state_name': state_name, 'station_number': station_number, 'zone_area': zone_area,
                 'parking_station_name': parking_station_name, 'bike_type': bike_type, 'published_on': published_on,
                 'status': 'published'})
    output.append({'parking_id': parking_id, 'city_name': city_name, 'city_id': city_id, 'state_id': state_id,
                   'state_name': state_name, 'station_number': station_number, 'zone_area': zone_area,
                   'parking_station_name': parking_station_name, 'bike_type': bike_type, 'published_on': published_on,
                   'status': 'published'})
    return jsonify({'status': "success", 'message': "uploaded successfully", 'result': output})


##################################parking_location_delete delete################################
@app.route('/smart_bike/parking_station_delete', methods=['POST', 'GET'])
def station_delete():
    try:
        data = client.smartbike_admin
        coll = data.bike_parking_details
        parking_id = request.json['parking_id']

        for q in coll.find({'parking_id': parking_id}):
            coll.remove({'parking_id': parking_id})

        return jsonify({'status': 'delete  successfully'})

    except Exception as e:
        return jsonify(status="fail", message=str(e))


@app.route('/smart_bike/address', methods=['POST', 'GET'])
def loc_address():
    try:
        data = client.smartbike_admin
        coll = data.smartbike_loc_address
        geolocator = Nominatim()
        address = request.json['address']
        country = request.json['country']
        loc = geolocator.geocode(address + ',' + country)

        # print("latitude is :-", loc.latitude, "\nlongtitude is:-", loc.longitude, "\naddress:", address)
        coll.insert({'address': address, 'latitude': loc.latitude, 'longitude': loc.longitude})
        return jsonify(
            {'status': 'True', 'message': 'address added successfully', 'address': address, 'latitude': loc.latitude,
             'longitude': loc.longitude})
    except Exception as e:
        return jsonify(status="fail", message=str(e))


@app.route('/smart_bike/loc_address', methods=['GET'])
def loc_adress():
    try:
        data = client.smartbike_admin
        coll = data.smartbike_loc_address
        details = coll.find()
        output = []
        for i in details:
            output.append({'address': i['address'], 'latitude': i['latitude'], 'longitude': i['longitude']})
        return jsonify({'status': True, 'results': output})
    except Exception as e:
        return jsonify(status="fail", message=str(e))


#######################################about_us#################################
@app.route('/smart_bike/upload_file/<id>/<file>', methods=['GET', 'POST'])
def upload_file_aboutus(id, file):
    data = client.smartbike_admin
    coll = data.smartbike_abouts
    # data = mongo.db.About_Fitzcube
    output = []

    if request.method == 'POST' and 'file' in request.files:
        for f in request.files.getlist('file'):
            os.makedirs(os.path.join(UPLOAD_FOLDER, str(file)), exist_ok=True)
            f.save(os.path.join(UPLOAD_FOLDER, str(file), secure_filename(f.filename)))
            file_path = os.path.join(UPLOAD_FOLDER, str(file), secure_filename(f.filename))
            coll.insert({"Id": int(id), "Type": file,
                         "Path": str(file_path.split("/")[-3]) + '/' + str(file_path.split("/")[-2]) + '/' + str(
                             file_path.split("/")[-1])})
            # coll.find_one_and_update({"Id": int(id)},{'$set':{"Type": file,"Path": str(file_path.split("/")[-3]) + '/' + str(file_path.split("/")[-2]) + '/' + str(file_path.split("/")[-1])}})
            output.append(str(file_path.split("/")[-3]) + '/' + str(file_path.split("/")[-2]) + '/' + str(
                file_path.split("/")[-1]))
        return jsonify({"status": "success", "output": output, "message": 'file saved successfully'})
    else:
        return jsonify({"status": "failure", "message": 'Error Occured, Please Try again'})


@app.route('/smart_bike/uplaod_files', methods=['GET'])
def uplaod_files():
    data = client.smartbike_admin
    coll = data.smartbike_abouts
    output = []
    for q in coll.find():
        output.append({'id': q['Id'], 'type': q['Type'], 'file_path': q['Path']})
    return jsonify({'status': 'success', 'message': 'About smartbike data get successfully', 'result': output})


# ########################encrypted data##########################
# @app.route('/encrypted', methods=['GET'])
# def encrypteddata():
#     key = get_random_bytes(16) # A 16 byte key for AES-128
#     nonce = get_random_bytes(15)
#     message = "A  really  secret message. Not for prying eyes.".encode()
#
#     cipher = AES.new(key, AES.MODE_OCB, nonce=nonce)
#     ciphertext, mac = cipher.encrypt_and_digest(message)
#     # ciphertext, mac = cipher.encrypt_and_digest()
#
#
#     cipher = AES.new(key, AES.MODE_OCB, nonce=nonce)
#     plaintext = cipher.decrypt_and_verify(ciphertext, mac)
#     a=b64encode(ciphertext).decode()
#     print(a)
#     #CSwHy3ir3MZ7yvZ4CzHbgYOsKgzhMqjq6wEuutU7vJJTJ0c38ExWkAY1QkLO
#     print(plaintext.decode())
#     #A really secret message. Not for prying eyes.
#     return a

############################places######################################
# @app.route('/smartbike/add_new_place',methods=['POST'])
# def add_new_place():
#     data = client.smartbike_admin
#     coll = data.smartbike_places
#     output=[]
#     try:
#         try:
#             place_name = request.json['place_name']
#         except KeyError or ValueError:
#             place_name = ""
#         try:
#             city_name = request.json['city_name']
#         except KeyError or ValueError:
#             city_name=""
#         try:
#             official_station = request.json['official_station']  ### tick T/F values
#         except KeyError or ValueError:
#             official_station=""
#         try:
#             tags = request.json['tags']
#         except KeyError or ValueError:
#             tags=""
#         try:
#             station_number = request.json['station_number']
#         except KeyError or ValueError:
#             station_number=""
#         try:
#             station_priority = request.json['station_priority']  # [1,2,3,4,5]
#         except KeyError or ValueError:
#             station_priority=""
#         try:
#             latitude = request.json['latitude']
#         except KeyError or ValueError:
#             latitude=""
#         try:
#             longitude = request.json['longitude']
#         except KeyError or ValueError:
#             longitude=""
#         try:
#             address = request.json['address']
#         except KeyError or ValueError:
#             address=""
#         try:
#             show_in_maps = request.json['show_in_maps']  ## tick,, T/F values
#         except KeyError or ValueError:
#             show_in_maps=""
#         try:
#             postal_code = request.json['postal_code']
#         except KeyError or ValueError:
#             postal_code=""
#         try:
#             setpoint_bikes = request.json['setpoint_bikes']
#         except KeyError or ValueError:
#             setpoint_bikes= ""
#         try:
#             booking_ratio = request.json['booking_ratio']
#         except KeyError or ValueError:
#             booking_ratio=""
#         try:
#             service_lead_time = request.json['service_lead_time']
#         except KeyError or ValueError:
#             service_lead_time=""
#         try:
#             max_bikes_for_reservation = request.json['max_bikes_for_reservation']
#         except KeyError or ValueError:
#             max_bikes_for_reservation=""
#         try:
#             bike_racks = request.json['bike_racks']
#         except KeyError or ValueError:
#             bike_racks=""
#         try:
#             bonus_minutes = request.json['bonus_minutes']
#         except KeyError or ValueError:
#             bonus_minutes=""
#         try:
#             place_type = request.json['place_type']  # [standard place, missed bikes, stolen bikes, storage etc]
#         except KeyError or ValueError:
#             place_type=""
#         try:
#             bike_rack_ids = request.json['bike_rack_ids']
#         except KeyError or ValueError:
#             bike_rack_ids=""
#         try:
#             special_racks = request.json['special_racks']
#         except KeyError or ValueError:
#             special_racks=""
#         try:
#             wpan_spot_snap_id = request.json['wpan_spot_snap_id']
#         except KeyError or ValueError:
#             wpan_spot_snap_id=""
#         try:
#             bikes_type_list = request.json['bikes_type_list']
#         except KeyError or ValueError:
#             bikes_type_list=""
#         # black/white
#         try:
#             set_bike_types_to_white = request.json['set_bike_types_to_white']
#         except KeyError or ValueError:
#             set_bike_types_to_white=""
#         try:
#             rack_fware_version = request.json['rack_fware_version']
#         except KeyError or ValueError:
#             rack_fware_version=""
#         # photos
#         try:
#             internal_comments = request.json['internal_comments']
#         except KeyError or ValueError:
#             internal_comments=""
#         try:
#             active_mode = request.json['active_mode']
#         except KeyError or ValueError:
#             active_mode=""
#         try:
#             active_maintenance = request.json['active_maintenance']
#         except KeyError or ValueError:
#             active_maintenance=""
#         place_id_list = [i['place_id'] for i in coll.find()]
#         if len(place_id_list) is 0:
#             place_id = 1
#         else:
#             place_id = int(place_id_list[-1]) + 1
#         bikes_types_list=['bike with low step','classic_bikes','electric_bike','accessories','bike_parking_spot']
#         coll.insert({'place_id': place_id, 'place_name': place_name, 'city_name': city_name,
#                      'official_station': official_station,
#                      'tags': tags, 'station_number': station_number, 'station_priority': station_priority,
#                      'latitude': latitude,
#                      'longitude': longitude, 'address': address, 'show_in_maps': show_in_maps,
#                      'postal_code': postal_code,
#                      'setpoint_bikes': setpoint_bikes, 'booking_ratio': booking_ratio,
#                      'service_lead_time': service_lead_time,
#                      'max_bikes_for_reservation': max_bikes_for_reservation, 'bike_racks': bike_racks,
#                      'bonus_minutes': bonus_minutes,
#                      'place_type': place_type, 'bike_rack_ids': bike_rack_ids, 'special_racks': special_racks,
#                      'wpan_spot_snap_id': wpan_spot_snap_id,
#                      'bikes_type_list': bikes_types_list, 'set_bike_types_to_white': set_bike_types_to_white,
#                      'rack_filmware_version': rack_fware_version,
#                      'internal_comments': internal_comments, 'active_mode': active_mode,
#                      'active_maintenance': active_maintenance})
#         output.append({'place_id': place_id, 'place_name': place_name, 'city_name': city_name,
#                        'official_station': official_station,
#                        'tags': tags, 'station_number': station_number, 'station_priority': station_priority,
#                        'latitude': latitude,
#                        'longitude': longitude, 'address': address, 'show_in_maps': show_in_maps,
#                        'postal_code': postal_code,
#                        'setpoint_bikes': setpoint_bikes, 'booking_ratio': booking_ratio,
#                        'service_lead_time': service_lead_time,
#                        'max_bikes_for_reservation': max_bikes_for_reservation, 'bike_racks': bike_racks,
#                        'bonus_minutes': bonus_minutes,
#                        'place_type': place_type, 'bike_rack_ids': bike_rack_ids, 'special_racks': special_racks,
#                        'wpan_spot_snap_id': wpan_spot_snap_id,
#                        'bikes_type_list': bikes_types_list, 'set_bike_types_to_white': set_bike_types_to_white,
#                        'rack_firmware_version': rack_fware_version,
#                        'internal_comments': internal_comments, 'active_mode': active_mode,
#                        'active_maintenance': active_maintenance})
#         return jsonify({'status': 'success', 'result': output, 'message': 'Place created successfully'})
#     except Exception as e:
#         return jsonify({'status': 'fail', 'result': [], 'message': str(e)})
######################################################
@app.route('/smart_bike/add_new_place', methods=['POST'])
def add_new_places():
    data = client.smartbike_admin
    coll = data.smartbike_places
    output = []
    geolocator = Nominatim()
    try:
        try:
            place_name = request.json['place_name']
        except KeyError or ValueError:
            place_name = ""
        try:
            city_name = request.json['city_name']
            city_id = int(request.json['city_id'])
        except KeyError or ValueError:
            city_name = ""
            city_id = ""
        try:
            state_name = request.json['state_name']
            state_id = int(request.json['state_id'])
        except KeyError or ValueError:
            state_name = ""
            state_id = ""
        try:
            official_station = request.json['official_station']
        except KeyError or ValueError:
            official_station = ""
        try:
            station_name = request.json['station_name']
        except KeyError or ValueError:
            station_name = ""
        try:
            country = request.json['country']
        except KeyError or ValueError:
            country = ""
        loc = geolocator.geocode(station_name + ',' + country)
        try:
            # loc = geolocator.geocode(station_name + ',' + country)
            loc = geolocator.geocode(station_name)
            print(loc.latitude, loc.longitude)
        except GeocoderTimedOut as e:
            print("Error")
        try:
            tags = request.json['tags']
        except KeyError or ValueError:
            tags = ""
        try:
            station_number = int(request.json['station_number'])
        except KeyError or ValueError:
            station_number = ""
        try:
            station_priority = request.json['station_priority']  # [1,2,3,4,5]
        except KeyError or ValueError:
            station_priority = ""
        try:
            show_in_maps = request.json['show_in_maps']  ## tick,, T/F values
        except KeyError or ValueError:
            show_in_maps = ""
        try:
            postal_code = int(request.json['postal_code'])
        except KeyError or ValueError:
            postal_code = ""
        try:
            setpoint_bikes = request.json['setpoint_bikes']
        except KeyError or ValueError:
            setpoint_bikes = ""
        try:
            booking_ratio = request.json['booking_ratio']
        except KeyError or ValueError:
            booking_ratio = ""
        try:
            service_lead_time = request.json['service_lead_time']
        except KeyError or ValueError:
            service_lead_time = ""
        try:
            max_bikes_for_reservation = request.json['max_bikes_for_reservation']
        except KeyError or ValueError:
            max_bikes_for_reservation = ""
        try:
            bike_racks = int(request.json['bike_racks'])
        except KeyError or ValueError:
            bike_racks = ""
        try:
            bonus_minutes = int(request.json['bonus_minutes'])
        except KeyError or ValueError:
            bonus_minutes = ""
        try:
            place_type = request.json['place_type']  # [standard place, missed bikes, stolen bikes, storage etc]
        except KeyError or ValueError:
            place_type = ""
        try:
            bike_rack_ids = int(request.json['bike_rack_ids'])
        except KeyError or ValueError:
            bike_rack_ids = ""
        try:
            special_racks = request.json['special_racks']
        except KeyError or ValueError:
            special_racks = ""
        try:
            wpan_spot_snap_id = int(request.json['wpan_spot_snap_id'])
        except KeyError or ValueError:
            wpan_spot_snap_id = ""
        try:
            total_no_of_bikes =int(request.json['total_no_of_bikes'])
        except KeyError or ValueError:
            total_no_of_bikes=""
        # # black/white
        try:
            set_bike_types_to_white = request.json['set_bike_types_to_white']
        except KeyError or ValueError:
            set_bike_types_to_white = ""
        try:
            rack_fware_version = request.json['rack_fware_version']
        except KeyError or ValueError:
            rack_fware_version = ""
        # photos
        try:
            internal_comments = request.json['internal_comments']
        except KeyError or ValueError:
            internal_comments = ""
        try:
            active_mode = request.json['active_mode']
        except KeyError or ValueError:
            active_mode = ""
        try:
            active_maintenance = request.json['active_maintenance']
        except KeyError or ValueError:
            active_maintenance = ""
        try:
            loc = geolocator.geocode(station_name + ',' + country)
            # loc = geolocator.geocode(station_name)
            print(loc.latitude, loc.longitude)
        except GeocoderTimedOut as e:
            print("Error")
        place_id_list = [i['place_id'] for i in coll.find()]
        if len(place_id_list) is 0:
            place_id = 1
        else:
            place_id = int(place_id_list[-1]) + 1
        bikes_types_list = ['bike with low step', 'classic_bikes', 'electric_bike', 'accessories', 'bike_parking_spot']
        coll.insert({'place_id': place_id, 'place_name': place_name, 'city_name': city_name, 'city_id': city_id,
                     'state_name': state_name, 'state_id': state_id,'total_no_of_bikes':total_no_of_bikes,
                     'tags': tags, 'station_number': station_number, 'station_priority': station_priority,
                     'official_station': official_station,
                     'latitude': loc.latitude, 'longitude': loc.longitude,
                     'station_name': station_name, 'show_in_maps': show_in_maps,
                     'postal_code': postal_code,
                     'setpoint_bikes': setpoint_bikes, 'booking_ratio': booking_ratio,
                     'service_lead_time': service_lead_time,
                     'max_bikes_for_reservation': max_bikes_for_reservation, 'bike_racks': bike_racks,
                     'bonus_minutes': bonus_minutes,
                     'place_type': place_type, 'bike_rack_ids': bike_rack_ids, 'special_racks': special_racks,
                     'wpan_spot_snap_id': wpan_spot_snap_id,
                     'bikes_types_list': bikes_types_list, 'set_bike_types_to_white': set_bike_types_to_white,
                     'rack_filmware_version': rack_fware_version,
                     'internal_comments': internal_comments, 'active_mode': active_mode,
                     'active_maintenance': active_maintenance})
        output.append({'place_id': place_id, 'place_name': place_name, 'city_name': city_name, 'city_id': city_id,
                       'state_name': state_name, 'state_id': state_id,
                       'tags': tags, 'station_number': station_number, 'station_priority': station_priority,
                       'latitude': loc.latitude, 'longitude': loc.longitude,
                       'station_name': station_name, 'show_in_maps': show_in_maps,
                       'postal_code': postal_code,
                       'setpoint_bikes': setpoint_bikes, 'booking_ratio': booking_ratio,
                       'service_lead_time': service_lead_time,'total_no_of_bikes':total_no_of_bikes,
                       'max_bikes_for_reservation': max_bikes_for_reservation, 'bike_racks': bike_racks,
                       'bonus_minutes': bonus_minutes, 'official_station': official_station,
                       'place_type': place_type, 'bike_rack_ids': bike_rack_ids, 'special_racks': special_racks,
                       'wpan_spot_snap_id': wpan_spot_snap_id,
                       'bikes_types_list': bikes_types_list, 'set_bike_types_to_white': set_bike_types_to_white,
                       'rack_firmware_version': rack_fware_version,
                       'internal_comments': internal_comments, 'active_mode': active_mode,
                       'active_maintenance': active_maintenance})
        return jsonify({'status': 'success', 'result': output, 'message': 'Place created successfully'})
    except Exception as e:
        return jsonify({'status': 'fail', 'result': [], 'message': str(e)})


UPLOAD = os.path.join(APP_ROOT, 'Places_Images')
if not os.path.exists(UPLOAD):
    os.makedirs(UPLOAD, exist_ok=True)
main_folder = os.path.join(APP_ROOT, UPLOAD)
app.config['UPLOAD_FOLDER'] = main_folder
# upload_folder = os.path.join(APP_ROOT, 'Places_Images')
# if not os.path.exists(upload_folder):
#     os.makedirs(upload_folder, exist_ok=True)
# main_folder = os.path.join(APP_ROOT, upload_folder)
# app.config['main_folder'] = main_folder


@app.route('/smart_bike/add_photos/<place_id>', methods=['POST'])
def add_photos(place_id):
    output = []
    data = client.smartbike_admin
    coll = data.smartbike_places
    files = []

    if request.method == 'POST' and 'file' in request.files:
        for f in request.files.getlist('file'):
            os.makedirs(os.path.join(main_folder, exist_ok=True))
            file_path = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
            # print(file_path)
            f.save(os.path.join(main_folder, secure_filename(f.filename)))
            # output.append(f.filename)
            files.append(file_path)
            # f.save(os.path.join(main_folder,str(file),secure_filename(f.filename)))
            file_path = os.path.join(main_folder,  secure_filename(f.filename))
        coll.find_one_and_update({'place_id': place_id}, {'$set': {'photos': files}})
        output.append({'place_id': place_id, 'photos': files})
        return jsonify({"status": "success", "output": output, "message": 'files saved successfully'})
    else:
        return jsonify({"status": "failure", "message": 'Error Occured, Please Try again'})


@app.route('/smart_bike/get_places', methods=['GET'])
def get_places():
    data = client.smartbike_admin
    coll = data.smartbike_places
    output = []
    try:
        for p in coll.find():
            output.append({'place_id': p['place_id'], 'place_name': p['place_name'], 'city_name': p['city_name'],
                           'official_station': p['official_station'], 'tags': p['tags'],
                           'station_number': p['station_number'], 'station_priority': p['station_priority'],
                           'latitude': p['latitude'], 'longitude': p['longitude'], 'address': p['address'],
                           'show_in_maps': p['show_in_maps'],
                           'postal_code': p['postal_code'], 'setpoint_bikes': p['setpoint_bikes'],
                           'booking_ratio': p['booking_ratio'],
                           'service_lead_time': p['service_lead_time'],
                           'max_bikes_for_reservation': p['max_bikes_for_reservation'], 'bike_racks': p['bike_racks'],
                           'bonus_minutes': p['bonus_minutes'],
                           'place_type': p['place_type'], 'bike_rack_ids': p['bike_rack_ids'],
                           'special_racks': p['special_racks'],
                           'wpan_spot_snap_id': p['wpan_spot_snap_id'],
                           'bikes_type_list': p['bikes_type_list'],'total_no_of_bikes':p['total_no_of_bikes'],
                           'set_bike_types_to_white': p['set_bike_types_to_white'],
                           'rack_firmware_version': p['rack_filmware_version'],
                           'internal_comments': p['internal_comments'], 'active_mode': p['active_mode'],
                           'active_maintenance': p['active_maintenance']})
        return jsonify({'status': 'success', 'message': 'Places listed successfully', 'output': output})
    except Exception as e:
        return jsonify({'status': 'fail', 'message': str(e), 'output': []})



###############################getting bikes details through bike_id####################
@app.route('/smart_bike/get_bike_details/<bike_id>', methods=['GET'])
def search32(bike_id):
     try:
        db = client.smartbike_admin
        data = db.smartbike_bike_details

        output = []

        for i in data.find({'bike_id':int(bike_id)}):
            id = i['bike_id']
            try:
                total_no_of_bikes = i['total_no_of_bikes']
            except KeyError or ValueError:
                total_no_of_bikes= ""
            try:
                updated_time = i['updated_time']
            except KeyError or ValueError:
                updated_time = ""
            # id = i['station_id']

            if int(id) == int(bike_id):
                bike_id = i['bike_id']

                output.append({'bike_id':id,'bike_frame_number':i['bike_frame_number'],'latitude':i['latitude'],'longitude':i['longitude'],'bike_type':i['bike_type'],'city_id':i['city_id'],
                                'state_id': i['state_id'], 'state_name': i['state_name'], 'city_name': i['city_name'], 'country': i['country'],
                               'bike_lock_type': i['bike_lock_type'], 'bike_make': i['bike_make'],  'bike_lock_number': i['bike_lock_number'],'total_no_of_bikes':total_no_of_bikes,'upload_bike_images': i['upload_bike_images'],
                               'upload_documents': i['upload_documents'],  'bike_racks': i['bike_racks'],  'bike_mode': i['bike_mode'],  'bike_color': i['bike_color'],'published_on': i['published_on'],'published_status': i['published_status'],
                               'Available_ride_date': i['Available_ride_date'],'date_of_purchase': i['date_of_purchase'],'updated_time':updated_time
                               })
        # output.append(bike_count)
        return jsonify({'status': 'success', 'message': 'list of bikes details in a station' ,'result': output})
     except Exception as e:
         return jsonify(status="Fail", message=str(e))

###########################################deleting bike-details#######################
@app.route('/smart_bike/bike_delete', methods=['POST', 'GET'])
def bike_delete():
    try:
        data = client.smartbike_admin
        coll = data.smartbike_bike_details
        bike_id = request.json['bike_id']

        for q in coll.find({'bike_id': bike_id}):
            coll.remove({'bike_id': bike_id})

        return jsonify({'status': 'delete  successfully'})

    except Exception as e:
        return jsonify(status="fail", message=str(e))


###############################edit_place#################################
@app.route('/smart_bike/edit_place', methods=['POST'])
def place_edit():
    data = client.smartbike_admin
    coll = data.smartbike_places
    output = []
    try:
        place_id = request.json['place_id']
        place_name = request.json['place_name']
        city_name = request.json['city_name']
        official_station = request.json['official_station']
        tags = request.json['tags']
        station_number = request.json['station_number']
        station_priority = request.json['station_priority']
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        address = request.json['address']
        show_in_maps = request.json['show_in_maps']
        postal_code = request.json['postal_code']
        setpoint_bikes = request.json['setpoint_bikes']
        booking_ratio = request.json['booking_ratio']
        service_lead_time = request.json['service_lead_time']
        max_bikes_for_reservation = request.json['max_bikes_for_reservation']
        bike_racks = request.json['bike_racks']
        bonus_minutes = request.json['bonus_minutes']
        place_type = request.json['place_type']
        bike_rack_ids = request.json['bike_rack_ids']
        bike_racks = request.json['bike_racks']
        special_racks = request.json['special_racks']
        wpan_spot_snap_id = request.json['wpan_spot_snap_id']
        bikes_type_list = request.json['bikes_type_list']
        set_bike_types_to_white = request.json['set_bike_types_to_white']
        rack_filmware_version = request.json['rack_filmware_version']
        internal_comments = request.json['internal_comments']
        active_mode = request.json['active_mode']
        active_maintenance = request.json['active_maintenance']
        total_no_of_bikes=int(request.json['total_no_of_bikes'])
        # updated_time = strftime("%Y/%m/%d %H:%M:%S %I%p")
        coll.update({'place_id': place_id},
                    {'$set': {'place_name': place_name, 'city_name': city_name, 'official_station': official_station,
                              'tags': tags, 'station_number': station_number, 'latitude': latitude,'total_no_of_bikes':total_no_of_bikes,
                              'longitude': longitude, 'address': address, 'show_in_maps': show_in_maps,
                              'postal_code': postal_code, 'setpoint_bikes': setpoint_bikes,
                              'station_priority': station_priority,
                              'booking_ratio': booking_ratio, 'service_lead_time': service_lead_time,
                              'max_bikes_for_reservation': max_bikes_for_reservation,
                              'bike_racks': bike_racks, 'bonus_minutes': bonus_minutes, 'place_type': place_type,
                              'bike_rack_ids': bike_rack_ids, 'special_racks': special_racks,
                              'wpan_spot_snap_id': wpan_spot_snap_id,
                              'bikes_type_list': bikes_type_list, 'set_bike_types_to_white': set_bike_types_to_white,
                              'rack_filmware_version': rack_filmware_version, 'internal_comments': internal_comments,
                              'active_mode': active_mode, 'active_maintenance': active_maintenance}})
        # output = []
        # details = coll.find()
        # for j in details:
        output.append({'place_id': place_id, 'place_name': place_name, 'city_name': city_name,
                       'official_station': official_station,
                       'tags': tags, 'station_number': station_number, 'latitude': latitude, 'longitude': longitude,
                       'address': address, 'show_in_maps': show_in_maps,
                       'postal_code': postal_code, 'setpoint_bikes': setpoint_bikes,
                       'station_priority': station_priority,
                       'booking_ratio': booking_ratio, 'service_lead_time': service_lead_time,
                       'max_bikes_for_reservation': max_bikes_for_reservation,
                       'bike_racks': bike_racks, 'bonus_minutes': bonus_minutes, 'place_type': place_type,
                       'bike_rack_ids': bike_rack_ids, 'special_racks': special_racks,
                       'wpan_spot_snap_id': wpan_spot_snap_id,'total_no_of_bikes':total_no_of_bikes,
                       'bikes_type_list': bikes_type_list, 'set_bike_types_to_white': set_bike_types_to_white,
                       'rack_filmware_version': rack_filmware_version, 'internal_comments': internal_comments,
                       'active_mode': active_mode, 'active_maintenance': active_maintenance
                       })
        return jsonify({'status': 'success', 'message': 'Profile updated successfully', 'result': output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))


# ######################bike_count################################
#
# @app.route('/smart_bike/bike_count', methods=['POST', 'GET'])
# def loc_address32():
#     try:
#         data = client.smartbike_admin
#         coll = data.smartbike_loc_address_count
#         coll1=data.bike_details
#         #station_id=request.json['station_id']
#         #geolocator = Nominatim()
#         output=[]
#         #address = request.json['address']
#         #country = request.json['country']
#         #loc = geolocator.geocode(address + ',' + country)
#         # print("latitude is :-", loc.latitude, "\nlongtitude is:-", loc.longitude, "\naddress:", address)
#         #
#         # coll.insert({'address': address, 'latitude': loc.latitude, 'longitude': loc.longitude})
#
#         cursor = coll1.aggregate([
#             {"$group": {
#                 "_id": {
#                     "station_id": "$station_id",
#                     "bike_id": "$bike_id"
#                 },
#                 "count": {"$sum": 1}
#             }},
#             {"$group": {
#                 "_id": "$_id.station_id",
#                 "results": {
#                     "$push": {
#                         "bike_id": "$_id.bike_id",
#                         #"station_id": "$_id.station_id",
#                         "count": "$count"
#                     }
#                 },
#                 "bike_count": {"$sum": "$count"}
#             }}
#         ])
#
#
#         #for j in coll.find({'station_id':station_id}):
#         for i in cursor:
#                     #output.append(i)
#             coll.insert({'bike_count':i['bike_count'],'station_id':i['_id']})
#                 #if j['station_id']==i['_id']:
#             #coll.update({'station_id':station_id},{'$set':{'bike_count':i['bike_count']}})
#             output.append({'bike_count':i['bike_count'],'station_id':i['_id']})
#                         #temp['bike_count']=i['bike_count']
#                     #temp['station_id']=i['_id']
#
#
#         return jsonify({'status': 'success', 'message': 'event dates get successfully', 'result': output})
#
#         #return jsonify(
#           #  {'status': 'True', 'message': 'address added successfully', 'address': address, 'latitude': loc.latitude,
#             # 'longitude': loc.longitude})
#     except Exception as e:
#             return jsonify(status="fail", message=str(e))
#
#
##################################get-status-management####################################
@app.route('/smart_bike/bike_status', methods=['GET'])
def bike_status():
    data = client.smartbike_admin
    coll = data.smartbike_bike_details
    output_list = []
    details = coll.find()
    for j in details:
        temp_dict = {}
        temp_dict['city_id'] = j['city_id']
        temp_dict['city_name'] = j['city_name']
        temp_dict['state_id'] = j['state_id']
        temp_dict['state_name'] = j['state_name']
        temp_dict['bike_type'] = j['bike_type']
        temp_dict['bike_color'] = j['bike_color']
        temp_dict['bike_lock_type'] = j['bike_lock_type']
        temp_dict['bike_id'] = j['bike_id']

        output_list.append(temp_dict)
    return jsonify({"status": "success", "message": "List of Profile", "result": output_list})


# @app.route('/moaisys/resumes', methods=['POST'])
# def get_resumes():
#     data = client.smartbike_admin
#     coll = data.moaisys_resumes
#     user_id = int
#     url ="http://103.248.211.205/ats/uat/api/resumes?user_id=" +  user_id
#     f = requests.get(url).json()
#     print(f)
#     return jsonify({'f':f})


######################################################### offer_management #####################################################

@app.route('/smart_bike/offer_management', methods=['POST'])
def offer_management():
    data = client.smartbike_admin
    coll = data.smartbike_offer_management
    coll2 = data.smartbike_admin_users

    # data = mongo.db.offer_management
    output = []
    try:
        voucher_name = str(request.json['voucher_name'])
        letters = string.ascii_uppercase
        stringLength = 2
        rand_alpha = ''.join(random.sample(letters, stringLength))
        voucher_code = voucher_name[:4] + str(random.randint(1000, 9999)) + rand_alpha
        print(voucher_code)

        # offer_title = request.json['offer_title']
        start_date = strftime('%Y-%m-%d')
        end_date = strftime('%Y-%m-%d')
        # deposit_amount = request.json['deposit_amount']
        cash_bonus = request.json['cash_bonus']
        # email_id = request.json['email_id']
        user_id = request.json['user_id']
        for i in coll2.find():
            ik = i['user_id']
            if int(ik) == int(user_id):
                coll.insert({'start_date': start_date, 'end_date': end_date,
                             'cash_bonus': cash_bonus, 'voucher_name': voucher_name, 'voucher_code': voucher_code,
                             'user_id': user_id})
                output.append({'start_date': start_date, 'end_date': end_date,
                               'cash_bonus': cash_bonus, 'voucher_name': voucher_name, 'voucher_code': voucher_code,
                               'user_id': user_id})
                return jsonify({'status': 'success', 'message': 'Offer added successfully', 'result': output})
        else:
            return jsonify({'status': 'failure', 'message': 'Invalid Admin_id'})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))





###############################edit_bike details#################################
@app.route('/smart_bike/edit_bike_details', methods=['POST'])
def bike_edit():
    data = client.smartbike_admin
    coll = data.smartbike_bike_details
    output = []
    try:
        bike_id = int(request.form['bike_id'])
        city_id = int(request.form['city_id'])
        city_name=request.form['city_name']
        state_id = int(request.form['state_id'])
        state_name = request.form['state_name']
        station_number = int(request.form['station_number'])
        station_name = request.form['station_name']
        latitude=request.form['latitude']
        longitude=request.form['longitude']
        country=request.form['country']
        bike_type=request.form['bike_type']
        bike_make=request.form['bike_make']
        bike_frame_number=request.form['bike_frame_number']
        bike_lock_number = request.form['bike_lock_number']
        bike_lock_type = request.form['bike_lock_type']
        bike_mode = request.form['bike_mode']
        bike_color = request.form['bike_color']
        total_no_of_bikes=int(request.form['total_no_of_bikes'])
        Available_ride_date = request.form['Available_ride_date']
        date_of_purchase = request.form['date_of_purchase']
        updated_time = strftime("%Y/%m/%d %H:%M:%S %I%p")
        upload_documents = []
        image_path1 = []
        upload_bike_images = []
        image_path = []
        if request.method == 'POST' and 'images' in request.files:
            for f in request.files.getlist('images'):
                # print(request.files.getlist)
                os.makedirs(os.path.join(UPLOAD_FOLDER), exist_ok=True)
                filename = secure_filename(f.filename)
                upload_bike_images.append(filename)
                # print(upload_image)
                mongo_db_path = "/Images/" + filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_path.append(mongo_db_path)
                f.save(filepath)
        if request.method == 'POST' and 'files' in request.files:
            for i in request.files.getlist('files'):
                # print(request.files.getlist)
                os.makedirs(os.path.join(UPLOAD_FOLDER), exist_ok=True)
                filename = secure_filename(i.filename)
                upload_documents.append(filename)
                # print(upload_image)
                mongo_db_path1 = "/Files/" + filename
                filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_path1.append(mongo_db_path1)
                i.save(filepath1)

        # updated_time = strftime("%Y/%m/%d %H:%M:%S %I%p")
        coll.update({'bike_id': bike_id},
                    {'$set': {'city_id': city_id, 'city_name': city_name, 'state_id': state_id,
                              'state_name': state_name, 'station_number': station_number,'latitude':latitude,'longitude':longitude,'station_name':station_name,'country':country,
                            'bike_type':bike_type, 'bike_make':bike_make, 'bike_frame_number': bike_frame_number,'total_no_of_bikes':total_no_of_bikes,
                              'bike_lock_number':bike_lock_number,'bike_lock_type':bike_lock_type,'bike_mode':bike_mode, 'upload_bike_images': image_path,
         'upload_documents': image_path1,
                              'bike_color':bike_color,'Available_ride_date':Available_ride_date,'date_of_purchase':date_of_purchase,'updated_time':updated_time}})
        # output = []
        # details = coll.find()
        # for j in details:
        output.append({'bike_id':bike_id,'city_id': city_id, 'city_name': city_name, 'state_id': state_id,
                              'state_name': state_name, 'station_number': station_number,'latitude':latitude,'longitude':longitude,'station_name':station_name,'country':country,
                            'bike_type':bike_type, 'bike_make':bike_make, 'bike_frame_number': bike_frame_number,'total_no_of_bikes':total_no_of_bikes,
                              'bike_lock_number':bike_lock_number,'bike_lock_type':bike_lock_type,'bike_mode':bike_mode, 'upload_bike_images': image_path,
         'upload_documents': image_path1,
                              'bike_color':bike_color,'Available_ride_date':Available_ride_date,'date_of_purchase':date_of_purchase,'updated_time':updated_time
                       })
        return jsonify({'status': 'success', 'message': 'bike details  updated successfully', 'result': output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

######################################################
@app.route('/smart_bike/add_new_places', methods=['POST'])
def add_new_places33():
    data = client.smartbike_admin
    coll = data.smartbike_places
    output = []
    try:
        try:
            station_number=int(request.json['station_number'])
        except KeyError or ValueError:
            station_number = ""
        try:
            place_name = request.json['place_name']
        except KeyError or ValueError:
            place_name = ""
        try:
            station_priority = request.json['station_priority']  # [1,2,3,4,5]
        except KeyError or ValueError:
            station_priority = ""
        try:
            show_in_maps = request.json['show_in_maps']  ## tick,, T/F values
        except KeyError or ValueError:
            show_in_maps = ""
        try:
            postal_code = int(request.json['postal_code'])
        except KeyError or ValueError:
            postal_code = ""
        try:
            max_bikes_for_reservation = request.json['max_bikes_for_reservation']
        except KeyError or ValueError:
            max_bikes_for_reservation = ""
        try:
            bike_racks = int(request.json['bike_racks'])
        except KeyError or ValueError:
            bike_racks = ""
        try:
            bonus_minutes = int(request.json['bonus_minutes'])
        except KeyError or ValueError:
            bonus_minutes = ""
        # try:
        #     place_type = request.json['place_type']  # [standard place, missed bikes, stolen bikes, storage etc]
        # except KeyError or ValueError:
        #     place_type = ""
        try:
            bike_rack_ids = int(request.json['bike_rack_ids'])
        except KeyError or ValueError:
            bike_rack_ids = ""
        try:
            active_mode = request.json['active_mode']
        except KeyError or ValueError:
            active_mode = ""
        try:
            active_maintenance = request.json['active_maintenance']
        except KeyError or ValueError:
            active_maintenance = ""

        coll.insert({'station_number': station_number, 'place_name': place_name,
                     # 'total_no_of_bikes':total_no_of_bikes,
                   'station_priority': station_priority,
                     'show_in_maps': show_in_maps,
                     'postal_code': postal_code,
                     'max_bikes_for_reservation': max_bikes_for_reservation, 'bike_racks': bike_racks,
                     'bonus_minutes': bonus_minutes,
                     'bike_rack_ids': bike_rack_ids,
                     # 'bikes_types_list': bikes_types_list,
                     'active_mode': active_mode,
                     'active_maintenance': active_maintenance})
        output.append({'station_number':station_number, 'place_name': place_name,
                     # 'total_no_of_bikes':total_no_of_bikes,
                    'station_priority': station_priority,
                     'show_in_maps': show_in_maps,
                     'postal_code': postal_code,
                     'max_bikes_for_reservation': max_bikes_for_reservation, 'bike_racks': bike_racks,
                     'bonus_minutes': bonus_minutes,
                     'bike_rack_ids': bike_rack_ids,
                     # 'bikes_types_list': bikes_types_list,
                     'active_mode': active_mode,
                     'active_maintenance': active_maintenance})
        return jsonify({'status': 'success', 'result': output, 'message': 'Place created successfully'})

    except Exception as e:
        return jsonify({'status': 'fail', 'result': [], 'message': str(e)})



###############################upload_bike details################

@app.route('/smart_bike/upload_bike', methods=['POST'])
def regis():
    data = client.smartbike_admin
    coll = data.smartbike_bike_details
    output = []
    try:
        city_id = int(request.json['city_id'])
        city_name = request.json['city_name']
        state_id = int(request.json['state_id'])
        state_name = request.json['state_name']
        station_number = int(request.json['station_number'])
        station_name = request.json['station_name']
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        country = request.json['country']
        bike_type = request.json['bike_type']
        bike_make = request.json['bike_make']
        bike_frame_number = int(request.json['bike_frame_number'])
        bike_lock_number = int(request.json['bike_lock_number'])
        bike_lock_type = request.json['bike_lock_type']
        bike_color = request.json['bike_color']
        bike_mode = request.json['bike_mode']
        published_on = strftime("%Y/%m/%d %H:%M:%S %I%p")
        Available_ride_date = request.json['Available_ride_date']
        date_of_purchase = request.json['date_of_purchase']
        bike_id_list = [i['bike_id'] for i in coll.find()]
        if len(bike_id_list) is 0:
            bike_id = 1
        else:
            bike_id = int(bike_id_list[-1]) + 1
        coll.insert({
            'bike_id': bike_id, 'city_name': city_name,  'state_id':state_id,
            'state_name': state_name,
            'station_number': station_number, 'station_name':station_name, 'bike_type': bike_type, 'bike_make': bike_make,
            'bike_frame_number': bike_frame_number, 'bike_lock_number': bike_lock_number, 'latitude': latitude, 'longitude': longitude,
            'bike_lock_type': bike_lock_type,
            'bike_mode': bike_mode, 'bike_color': bike_color, 'country': country, 'published_on': published_on,
            'published_status': 'published', 'Available_ride_date': Available_ride_date,'city_id':city_id,
            'date_of_purchase': date_of_purchase})
        output.append(
                    {'bike_id': bike_id, 'city_name': city_name,  'state_id':state_id,
                     'state_name': state_name,
                     'station_number': station_number, 'station_name': station_name, 'bike_type': bike_type, 'bike_make': bike_make,
                     'bike_frame_number': bike_frame_number, 'bike_lock_number': bike_lock_number,'latitude':latitude,'longitude':longitude,
                     'bike_lock_type': bike_lock_type,
                     'bike_mode': bike_mode, 'bike_color': bike_color, 'country':country,'published_on': published_on,
                     'published_status': 'published', 'Available_ride_date': Available_ride_date,'city_id':city_id,
                     'date_of_purchase': date_of_purchase})
        return jsonify({'status': 'success', 'message': 'bike_details uploaded successfully', 'result': output})


    except Exception as e:
        return jsonify(status="Fail", message=str(e))


##################customer_info#########################
@app.route('/smart_bike/get_customer_info', methods=['GET'])
def get_details41():
    try:
        db = client.smart_bike
        coll = db.smart_bike_users
        output = []
        for q in coll.find():
            output.append({'user_id': q['user_id'], 'user_name': q['user_name'], 'first_name': q['first_name'],
                           'last_name': q['last_name'],
                           'mobile_number': q['mobile_number'], 'email_id': q['email_id'], 'kyc_status': q['kyc_status']})
        return jsonify({'status': 'success', 'message': 'all user details', "result": output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))
###########################get_kyc#####################################
@app.route('/smart_bike/customer_details/kyc_status/is_true', methods=['GET'])
def customer_kyc_details():
    db = client.smart_bike
    coll = db.smart_bike_users
    output_list = []
    details = coll.find()
    for u_id in details:  # here u_id is the iteration variable to check the all users in database
        ks = u_id['kyc_status']
        if ks == True:
            # print(ks)
            # exit()
            temp_dict = {}
            temp_dict['user_id'] = u_id['user_id']
            temp_dict['user_name'] = u_id['user_name']
            temp_dict['first_name'] = u_id['first_name']
            temp_dict['last_name'] = u_id['last_name']
            temp_dict['mobile_number'] = u_id['mobile_number']
            temp_dict['email_id'] = u_id['email_id']
            temp_dict['kyc_status'] = u_id['kyc_status']
            try:
                temp_dict['login_type'] = u_id['login_type']
            except KeyError or ValueError:
                temp_dict['login_type'] = ""

            output_list.append(temp_dict)
            # return jsonify({"status": "success", "message": "List of Profile", "result": output_list})
        # else:
        #     return jsonify({"status": "fail", "message": "List of Profile", "result": output_list})
    return jsonify({"status": "success", "message": "success", "result": output_list})

########################################get_places####################################
@app.route('/smart_bike/places_get', methods=['GET'])
def get_places_api():
    try:
       db = client.smartbike_admin
       coll = db.smartbike_places
       output_list = []
       details = coll.find()
       for i in details:  # here u_id is the iteration variable to check the all users in database

            station_number = i['station_number']
            place_name = i['place_name']
            station_priority = i['station_priority']
            bike_racks = i['bike_racks']
            active_mode=i['active_mode']
            max_bikes_for_reservation = i['max_bikes_for_reservation']
            output_list.append({'station_number':station_number,'place_name':place_name,'station_priority':station_priority,'bike_racks':bike_racks,'max_bikes_for_reservation':max_bikes_for_reservation,'active_mode':active_mode})
            return jsonify({"status": "success", "message": "success", "result": output_list})
       else:
           return jsonify({"status":"fail","message":"failed to upload"})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))


############################get_places__station_number#####################################
@app.route('/smart_bike/places_get/<station_number>', methods=['GET'])
def get_places_stnum(station_number):
    db = client.smartbike_admin
    coll = db.smartbike_places
    output_list = []
    details = coll.find()
    for i in details:  # here u_id is the iteration variable to check the all users in database

            station_number = i['station_number']
            place_name = i['place_name']
            station_priority = i['station_priority']
            bike_racks = i['bike_racks']
            active_mode=i['active_mode']
            max_bikes_for_reservation = i['max_bikes_for_reservation']
            output_list.append({'station_number':station_number,'place_name':place_name,'station_priority':station_priority,'bike_racks':bike_racks,'max_bikes_for_reservation':max_bikes_for_reservation,'active_mode':active_mode})
    return jsonify({"status": "success", "message": "success", "result": output_list})

############################get_places_edit#################################################
@app.route('/smart_bike/places_edit/<station_number>', methods=['POST'])
def places_edit(station_number):
    db = client.smartbike_admin
    coll = db.smartbike_places
    place_name = request.json['place_name']
    output_list = []
    details = coll.find()
    for i in details:
        coll.update({'station_number': station_number}, {'$set': {'place_name': place_name}})
        output_list.append({'station_number':station_number,'place_name':i['place_name'],'station_priority':i['station_priority'],'bike_racks':i['bike_racks'],
                            'max_bikes_for_reservation':i['max_bikes_for_reservation'],'active_mode':i['active_mode']})
    return jsonify({"status": "success", "message": "success", "result": output_list})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001, debug=True, threaded=True)
    # app.run(debug=True, threaded=True)


