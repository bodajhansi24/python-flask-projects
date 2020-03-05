import base64
import math
import os
import random
from time import strftime

# import pyqrcode as pyqrcode
# import png
import requests
# import bcrypt
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from flask_cors import CORS
from random import randint
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token)
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
import http.client
from flask_login import login_user, logout_user, login_required, LoginManager
import re
from flask import Flask, render_template, url_for, request, redirect, jsonify, json, session, flash
from pymongo import MongoClient
# import pyqrcode
# import png
import jinja2
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import flask_login
from flask_login import login_user, logout_user, login_required, LoginManager
from flask import Flask, session, redirect, url_for

import logging
import time

logging.getLogger(__name__).addHandler(logging.NullHandler())
from bson.json_util import dumps


app = Flask(__name__)

client = MongoClient('35.154.239.192:6909')
# lient = MongoClient('localhost')
# print(client)

app.config['MONGO_DBNAME'] = 'smart_bike'
# app.config['MONGO_URI']='mongodb://35.154.239.192/smart_bike'
app.config['MONGO_URI'] = 'mongodb://35.154.239.192:6909/smart_bike'
app.config['JWT_SECRET_KEY'] = 'fugenx'

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

mail = Mail(app)

CORS(app,supports_credentials= True)



@app.route('/send_mail', methods=['POST'])
def email_send():
    email_id = request.json['email_id']
    msg = Message('Welcome to smart_bike', sender="indiral@fugenx.com", recipients=[email_id])
    msg.body = 'Thank you for registering with us.\n\n\n For any queries please feel free to drop us an email\n\n\n Thankyou'
    mail.send(msg)


################################## register ######################################
@app.route('/smart_bike/register', methods=['POST'])
def register():
    db = client.smart_bike
    coll = db.smart_bike_users
    try:
        user_name = request.json['user_name']
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        try:
            email_id = request.json['email_id']
        except KeyError or ValueError:
            email_id = ""
        password = request.json['password']
        confirm_password = request.json['confirm_password']
        if password != confirm_password:
            return "Passwords do not match. try again"
        referal_code = request.json['referal_code']
        session_id = request.json['session_id']
        kyc_status = False
        # kyc_status=request.json['kyc_status']
        otp_value = str(randint(1000, 9999))
        if password != confirm_password:
            return "Passwords do not match. try again"
        mobile_number = request.json['mobile_number']
        access_token = create_access_token(identity=email_id)
        created_time = strftime("%Y/%m/%d %H:%M:%S %I%p")
        # kyc_status=[]
        try:
            msg = Message('Welcome to smart_bike', sender="saranmai.k@fugenx.com", recipients=[email_id])
            msg.body = 'Thank you for registering with us.\n\n\n For any queries please feel free to drop us an email\n\n\n Thankyou\n Team smartbike'
            mail.send(msg)
        except:
            pass

        user_id_list = [i['user_id'] for i in coll.find()]
        if len(user_id_list) is 0:
            user_id = 1
        else:
            user_id = int(user_id_list[-1]) + 1
        er = coll.find({'email_id': email_id})
        mr = coll.find({'mobile_number': mobile_number})

        for m in mr:
            if m['mobile_number'] == mobile_number:
                return jsonify({'status': 'false',
                                'message': 'Seems like you have already registered wth us.Please login to continue.'})

        for j in er:
            if j['email_id'] == email_id:
                return jsonify({'status': 'false',
                                'message': 'Seems like you have already registered wth us.Please login to continue.'})
        url = "https://api.msg91.com/api/sendhttp.php?mobiles=" + mobile_number + "&authkey=298368AqfT6kZfwqB55da04dbf&route=4&sender=SMTBYK&message=Your OTP IS" + ' ' + str(
            otp_value) + "&country=91"
        f = requests.get(url)
        if re.match(pattern=r'(^(0/91))?([0-9]{10}$)', string=mobile_number):  # check for mobilenumber properly
            if re.match(r'[A-Za-z0-9@#$%^&+=]{1,12}', password):  # check for password properly
                # flash('Your OTP:' + otp_value)

                output = []
                coll.insert(
                    {'user_name': user_name, 'first_name': first_name, 'last_name': last_name, 'email_id': email_id,
                     'password': password, 'session_id': session_id,'confirm_password':confirm_password,
                     'user_id': user_id, 'OTP': otp_value,
                     'mobile_number': mobile_number, 'created_time': created_time, 'referal_code': referal_code,
                     'kyc_status': kyc_status
                     })
                output.append(
                    {'user_name': user_name, 'first_name': first_name, 'last_name': last_name, 'email_id': email_id,
                     'password': password, 'session_id': session_id,'confirm_password':confirm_password,
                    'user_id': user_id, 'OTP': otp_value,
                     'mobile_number': mobile_number, 'created_time': created_time, 'kyc_status': kyc_status,
                     'referal_code': referal_code})
                return jsonify({'status': 'true', 'message': 'User is registered', 'result': output})
            else:
                return jsonify({'status': 'false', 'message': 'Invalid Password.'})
        else:
            return jsonify({'status': 'false', 'message': 'Invalid Mobile Number'})

    except Exception as e:
        return jsonify(status="False", message=str(e))



############################### login #######################################
@app.route('/smart_bike/login', methods=['POST'])
def login():
    db = client.smart_bike
    coll = db.smart_bike_users
    user_name = request.json['user_name']
    password = request.json['password']
    login_type = request.json['login_type']

    access_token = create_access_token(identity=user_name)
    # check_pwd=bcrypt.check_password_hash(password)
    # print(check_pwd)
    details = coll.find_one_and_update({'mobile_number': user_name, 'password': password}, {'$set': {'login_type':login_type}})

    info = coll.find_one_and_update({'email_id': user_name, 'password': password}, {'$set': {'login_type':login_type}})
    d = coll.find({'mobile_number': user_name, 'password': password})
    inf = coll.find({'email_id': user_name, 'password': password})
    output = []
    for j in d:
        output.append({'user_id': j['user_id'], 'user_name': j['user_name'], 'email_id': j['email_id'],
                       'first_name': j['first_name'], 'last_name': j['last_name'],
                      # 'select_city': j['select_city'],'upload_img_path': j['upload_img_path'],
                       'mobile_number': j['mobile_number'], 'session_id': j['session_id'],
                       'created_time': j['created_time']})
    for i in inf:
        output.append({'user_id': i['user_id'], 'user_name': i['user_name'], 'email_id': i['email_id'],
                       'first_name': i['first_name'], 'last_name': i['last_name'],
                      # 'select_city': i['select_city'],'upload_img_path': i['upload_img_path'],
                       'mobile_number': i['mobile_number'], 'session_id': i['session_id'],
                       'created_time': i['created_time']})
        #
    finaloutput = {}
    if len(output) != 0:
        finaloutput['status'] = 'true'
        finaloutput['message'] = 'login Successful'
        finaloutput['result'] = output
        finaloutput['token'] = access_token
    else:
        finaloutput['status'] = 'false'
        finaloutput['message'] = 'Invalid Credentials. Please check and try again'
        finaloutput['result'] = []
    return jsonify(finaloutput)
###########
#
# @app.route('/smart_bike/register_otp', methods=['POST'])
# def register_otp():
#     try:
#         db = client.smart_bike
#         coll = db.smart_bike_users
#         mobile_number = request.json['mobile_number']
#         print(mobile_number)
#         data = coll.find({'mobile_number': mobile_number})
#         for d in data:
#             print(d['mobile_number'])
#             if d['mobile_number'] == mobile_number:
#                 otp_value = str(randint(1000, 9999))
#                 print(otp_value)
#                 flash('Your OTP:' + otp_value)
#             coll.find_one_and_update({'mobile_number': mobile_number}, {'$set': {'OTP': otp_value}})
#             return jsonify({'status': "true", "message": "OTP generated successfully", "OTP": otp_value})
#         else:
#             return jsonify({'status': "false", "message": "Please enter your registered mobile number"})
#     except Exception as e:
#         return jsonify(status="false", message=str(e))

############################# ReSend Otp######################################
@app.route('/smart_bike/resend_otp', methods=['POST'])
def Reg_OTP():
    try:
        db = client.smart_bike
        coll = db.smart_bike_users
        mobile_number = str(request.json['mobile_number'])
        if coll.find_one({'mobile_number': mobile_number}) is not None:
            register = mongo.db.register
            otp_value = randint(1000, 9999)
            flag = 0
            if len(mobile_number) is 10:
                flag = 1
                mobile_number = "+91" + " " + str(mobile_number)
            if flag == 1:
                mobile_number = mobile_number.split(' ')[1]
                url = "https://api.msg91.com/api/sendhttp.php?mobiles=" + mobile_number + "&authkey=293844AlhYRFCo5d7b2d94&route=4&sender=SMTBYK&message=Your OTP IS" + ' ' + str(
                    otp_value) + "&country=91"
                f = requests.get(url)
            register.find_one_and_update({'mobile_number': mobile_number},{'$set':{'OTP': str(otp_value)}})
            return jsonify({'status': "success", "message": "OTP generated successfully","OTP":str(otp_value)})
        else:
            return jsonify({'status': "failure", "message": "MobileNumber entered is not in the Database.Please enter registered mobilenumber!!!"})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))


########################################### verify-otp ##############################
@app.route('/smart_bike/verify_otp/<user_id>', methods=['POST'])
def verify_otp(user_id):
    try:
        db = client.smart_bike
        coll = db.smart_bike_users
        otp_entered = str(request.json['otp_entered'])
        mobile_number = str(request.json['mobile_number'])
        output = []
        details = coll.find({'mobile_number': str(mobile_number), 'OTP': str(otp_entered)})
        for j in details:
            otp = j['OTP']
            if otp == otp_entered:
                output.append({'user_id': j['user_id'], 'user_name': j['user_name'], 'email_id': j['email_id'],
                               'password': j['password'],
                               'mobile_number': j['mobile_number'], 'otp_entered': j['OTP'], 'Verified': 1,
                               'created_time': j['created_time']})
            else:
                coll.remove({'user_id': user_id})
                # print(user_id)
        finaloutput = {}
        if len(output) != 0:
            finaloutput['status'] = 'true'
            finaloutput['message'] = 'user data found'
            finaloutput['result'] = output
        else:
            finaloutput['status'] = 'false'
            finaloutput['message'] = 'Invalid OTP. Please check and try again'
            finaloutput['result'] = []
        return jsonify(finaloutput)
    except Exception as e:
        return jsonify(status="False", message=str(e))


# @app.route('/smart_bike/resend_otp', methods=['POST'])
# def resend_otp():
#     try:
#         db = client.smart_bike
#         coll = db.smart_bike_users
#         mobile_number = str(request.json['mobile_number'])
#         if coll.find_one({'mobile_number': mobile_number}) is not None:
#             register = mongo.db.register
#             otp_value = randint(1000, 9999)
#             flag = 0
#             if len(mobile_number) is 10:
#                 flag = 1
#                 mobile_number = "+91" + " " + str(mobile_number)
#             if flag == 1:
#                 mobile_number = mobile_number.split(' ')[1]
#                 url = "https://api.msg91.com/api/sendhttp.php?mobiles=" + mobile_number + "&authkey=293844AlhYRFCo5d7b2d94&route=4&sender=SMTBYK&message=Your OTP IS" + ' ' + str(
#                     otp_value) + "&country=91"
#                 f = requests.get(url)
#                 coll.find_one_and_update({'mobile_number': mobile_number},{'$set':{'OTP': str(otp_value)}})
#                 return jsonify({'status': "success", "message": "OTP generated successfully","OTP":str(otp_value)})
#             else:
#                 return jsonify({'status': "failure", "message": "MobileNumber entered is not in the Database.Please enter registered mobilenumber!!!"})
#     except Exception as e:
#         return jsonify(status="Fail", message=str(e))
############################### forgot-password #######################################
@app.route('/smart_bike/forgot_password', methods=['POST'])
def forgot_password():
    try:
        db = client.smart_bike
        coll = db.smart_bike_users
        mobile_number = str(request.json['mobile_number'])
        if coll.find_one({'mobile_number': mobile_number}) is not None:
            otp_value = randint(1000, 9999)
            url = "https://api.msg91.com/api/sendhttp.php?mobiles=" + mobile_number + "&authkey=298368AqfT6kZfwqB55da04dbf&route=4&sender=SMTBYK&message=Your OTP IS" + ' ' + str(
                otp_value) + "&country=91"
            f = requests.get(url)
            flag = 0
            if len(mobile_number) is 10:
                flag = 1
                mobile_number = "+91" + " " + str(mobile_number)
            if flag == 1:
                mobile_number = mobile_number.split(' ')[1]
            coll.find_one_and_update({'mobile_number': mobile_number},{'$set':{'OTP': str(otp_value)}})
            return jsonify({'status': "success", "message": "OTP generated successfully","OTP":str(otp_value)})
        else:
            return jsonify({'status': "failure", "message": "MobileNumber entered is not in the Database.Please enter registered mobilenumber!!!"})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

#############################################change password#####################################
# @app.route('/smart_bike/change_password', methods=['POST'])
# def change_password():
#     try:
#         db = client.smart_bike
#         coll = db.smart_bike_users
#         # register = mongo.db.register
#         password = str(request.json['changed_password'])
#         # changed_password=str(request.json['confirm_password'])
#         mobile_number = str(request.json['mobile_number'])
#         coll.find_one_and_update({'mobile_number': mobile_number}, {'$set': {'password': password}})
#         return jsonify({'status': 'success', "message": "password changed successfully", 'password': password})
#     except Exception as e:
#         return jsonify(status="Fail", message=str(e))
#
############################### change-password #######################################
# @app.route('/smart_bike/change_password', methods=['POST','GET'])
# def reset_password():
#     db = client.smart_bike
#     coll = db.smart_bike_users
#     user_id= request.json['user_id']
#     new_password = str(request.json['new_password'])
#     confirm_password = str(request.json['confirm_password'])
#     try:
#         if new_password!=confirm_password:
#             return "Please enter the same passwords."
#         data= coll.find()
#         for d in data:
#             id= int(user_id)
#             if d['user_id']==id:
#                 coll.find_one_and_update({'user_id': id}, {'$set': {'password': new_password, 'confirm_password':new_password}})
#                 return jsonify({'status': 'success', 'message': 'password changed successfully','password':new_password})
#         else:
#             return jsonify({'status':'fail','message':'Failed to reset password. Please try again'})
#     except Exception as e:
#         return jsonify({'status':'fail','result':str(e)})
################################ change-password ######################################
@app.route('/smart_bike/change_password', methods=['POST', 'GET'])
def reset_password():
    db = client.smart_bike
    coll = db.smart_bike_users
    mobile_number = request.json['mobile_number']
    new_password = str(request.json['new_password'])
    confirm_password = str(request.json['confirm_password'])
    output = []
    try:
        if new_password != confirm_password:
            return "Please enter the same passwords."
        data = coll.find()
        for i in data:
            mn = i['mobile_number']
            id = i['user_id']
            if mn == mobile_number:
                coll.find_one_and_update({'mobile_number': mn},
                                         {'$set': {'password': new_password, 'confirm_password': new_password}})
                output.append({'user_id': id})
                return jsonify({'status': 'success', 'message': 'password changed successfully', 'result': output})
        else:
            return jsonify({'status': 'fail', 'message': 'Failed to reset password. Please try again'})
    except Exception as e:
        return jsonify({'status': 'fail', 'result': str(e)})

# @app.route('/logout')
# def logout():
#     session.pop('email', None)
#     return redirect('/

############################### kyc-management ############################################
@app.route('/smart_bike/kyc', methods=['POST', 'GET'])
def add_id_proof():
    db = client.smart_bike
    coll = db.smart_bike_users
    # print(coll)
    output = []
    user_id = int(request.json['user_id'])
    id_proof = request.json['id_proof']
    id_proof_num=request.json['id_proof_num']
    front_image = request.json['front_image']
    front_image = front_image.encode()
    back_image = request.json['back_image']
    back_image = back_image.encode()
    date_of_upload = strftime("%Y/%m/%d %H:%M:%S %I%p")
    date_of_verified = strftime("%Y/%m/%d %H:%M:%S %I%p")
    kyc_status = True
    # filename= secure_filename(photo.filename)
    # print(filename)
    front_image_path = '/var/www/html/smartbike/Images/'+ 'front'+str(user_id)+'.jpg'
    mongo_db_front_image_path = "/smartbike/Images/" + 'front'+str(user_id)+'.jpg'
    # front_image_path = '/var/www/html/smartbike/Images/' + 'front' + str(user_id)
    # print(front_image_path)
    back_image_path = '/var/www/html/smartbike/Images/'+ 'back'+str(user_id)+'.jpg'
    mongo_db_back_image_path = "/smartbike/Images/" + 'back'+str(user_id)+'.jpg'
    # back_image_path = '/var/www/html/smartbike/Images/' + 'back' + str(user_id)
    with open(front_image_path, 'wb') as f:
        f.write(base64.decodebytes(front_image))
    with open(back_image_path, 'wb') as f:
        f.write(base64.decodebytes(back_image))
    data = coll.find()
    for d in data:
        id = d['user_id']
        # print(id)
        if int(id) == int(user_id):
            # print(d['user_id'])
            if (kyc_status == True):
                coll.find_one_and_update({'user_id': user_id}, {
                    '$set': {'id_proof': id_proof, 'front_image_path': mongo_db_front_image_path,
                             'back_image_path': mongo_db_back_image_path, 'kyc_status': kyc_status,
                             'date_of_upload': date_of_upload,'id_proof_num':id_proof_num,
                             'date_of_verified': date_of_verified}})
                # output.append({'user_id': user_id, 'upload_pic_path': upload_pic_path})
                #     coll.update({'user_id': user_id}, {'$set': {'front_image_path': front_image_path, 'id_proof': id_proof,
                #                          'back_image_path': back_image_path,
                #                          'date_of_upload': date_of_upload, 'date_of_verified': date_of_verified,
                #                          'kyc_status':kyc_status}})
                output.append(
                    {'user_id': user_id, 'id_proof': id_proof, 'front_image_path': mongo_db_front_image_path,
                     'back_image_path': mongo_db_back_image_path, 'kyc_status': kyc_status,'id_proof_num':id_proof_num,
                     'date_of_upload': date_of_upload, 'date_of_verified': date_of_verified
                     })
                return jsonify({'result': output, 'message':'kyc details updated successfully','status': 'true'})
    else:
        return "Error"

############################### kyc-edit ############################################
@app.route('/smart_bike/edit_kyc', methods=['POST', 'GET'])
def edit_kyc():
    db = client.smart_bike
    coll = db.smart_bike_users
    # print(coll)
    output = []
    user_id = int(request.json['user_id'])
    id_proof = request.json['id_proof']
    id_proof_num = request.json['id_proof_num']
    front_image = request.json['front_image']
    front_image = front_image.encode()
    back_image = request.json['back_image']
    back_image = back_image.encode()
    date_of_upload = strftime("%Y/%m/%d %H:%M:%S %I%p")
    date_of_verified = strftime("%Y/%m/%d %H:%M:%S %I%p")
    st = randint(1000, 9999)
    # st = strftime("%H:%M:%S %I%p")
    kyc_status = True
    front_image_path = '/var/www/html/smartbike/Images/' + 'front'+str(user_id)+str(st)+'.jpg'
    mongo_db_front_image_path = "/smartbike/Images/" + 'front' +str(user_id)+ str(st) + '.jpg'
    # front_image_mongo_db_path = '/Images/' + str(user_id) + '.' + 'jpg'
    back_image_path = '/var/www/html/smartbike/Images/' + 'back'+str(user_id)+str(st)+'.jpg'
    mongo_db_back_image_path = "/smartbike/Images/" + 'back' + str(user_id) + str(st) + '.jpg'
    # back_image_mongo_db_path = '/Images/' + str(user_id) + '.' + 'jpg'
    with open(front_image_path, 'wb') as f:
        f.write(base64.decodebytes(front_image))
    with open(back_image_path, 'wb') as f:
        f.write(base64.decodebytes(back_image))
    data = coll.find()
    for d in data:
        id = d['user_id']
        # print(id)
        if int(id) == int(user_id):
            # print(d['user_id'])
            if (kyc_status == True):
                coll.update({'user_id': user_id}, {
                    '$set': {'id_proof': id_proof, 'front_image_path': mongo_db_front_image_path, 'kyc_status': kyc_status, 'back_image_path': mongo_db_back_image_path,
                             'date_of_upload': date_of_upload,'id_proof_num':id_proof_num,
                             'date_of_verified': date_of_verified}})

                output.append(
                    {'user_id': user_id, 'id_proof': id_proof, 'front_image_path': mongo_db_front_image_path,
                     'back_image_path': mongo_db_back_image_path, 'kyc_status': kyc_status,'id_proof_num':id_proof_num,
                     'date_of_upload': date_of_upload, 'date_of_verified': date_of_verified
                     })
                return jsonify({'result': output, 'status': 'true', 'message': ' kyc details updated successfully'})
    else:
        return jsonify({"status": "fail", 'message': 'please try again.....!'})


################################ delete-kyc ###########################
@app.route('/smart_bike/delete_kyc', methods=['POST', 'GET'])
def delete_kyc():
    db = client.smart_bike
    coll = db.smart_bike_users
    # print(coll)
    output = []
    user_id = request.json['user_id']
    try:
        data = coll.find()
        for d in data:
            id = d['user_id']
            if str(id) == str(user_id):
                coll.update({'user_id': int(user_id)}, {'$unset': {'front_image': 1, 'back_image': 1, 'id_proof': 1,'id_proof_num':1,
                                                                   'date_of_upload': 1, 'date_of_verified': 1}})
                coll.find_one_and_update({'user_id': int(user_id)}, {'$set': {'kyc_status': False}})
                output.append({'user_id': int(user_id)})
                return jsonify({'status': 'success', 'message': 'updated kyc successfully', 'result': output})
    except Exception as e:
        return jsonify({'status': 'fail', 'result': str(e)})



############################### social-login #########################################
@app.route('/smart_bike/social_login', methods=['POST', 'GET'])
def social_login():
    result = []
    user_name = request.json['user_name']
    email_id = str(request.json['email_id'])
    google_id = request.json['google_id']
    facebook_id = request.json['facebook_id']
    profile_pic = request.json['profile_pic']
    login_type = request.json['login_type']
    register = mongo.db.smart_bike_users
    if google_id != "":
        q = register.find_one_and_update({'google_id': google_id}, {'$set': {'login_type': login_type}})
    elif facebook_id != "":
        q = register.find_one_and_update({'facebook_id': facebook_id}, {'$set': {'login_type': login_type}})
    if (q != None) and (google_id != "" or facebook_id != ""):
        user_id = None
        temp_dict = {}
        temp_dict['user_id'] = q['user_id']
        user_id = q['user_id']
        temp_dict['user_name'] = q['user_name']
        temp_dict['email_id'] = q['email_id']
        if google_id != "":
            temp_dict['google_id'] = q['google_id']
        elif facebook_id != "":
            temp_dict['facebook_id'] = q['facebook_id']
        result.append(temp_dict)
        return jsonify({"status": "true", "message": "Login Successful", "result": result})

    else:
        data = register.find({'email_id': email_id})
        user_id = [i['user_id'] for i in register.find()]
        if len(user_id) is 0:
            user_id_value = 1
        else:
            user_id_value = int(str(user_id[-1])) + 1
        if data.count() != 0:
            return jsonify({'status': 'false', 'message': 'User is already registered',"result": result})
        elif google_id != "":
            register.insert({'user_id': user_id_value, 'user_name': user_name, 'email_id': email_id, 'facebook_id': "",
                             'google_id': google_id, "profile_pic": profile_pic})
            q = register.find_one({'google_id': google_id})
        elif facebook_id != "":
            register.insert(
                {'user_id': user_id_value, 'user_name': user_name, 'email_id': email_id, 'facebook_id': facebook_id,
                 'google_id': google_id, "profile_pic": profile_pic})
            q = register.find_one({'facebook_id': facebook_id})
        temp_dict = {}
        temp_dict['user_id'] = q['user_id']
        temp_dict['user_name'] = q['user_name']
        temp_dict['email_id'] = q['email_id']
        if google_id != "":
            temp_dict['google_id'] = q['google_id']
        elif facebook_id != "":
            temp_dict['facebook_id'] = q['facebook_id']
        result.append(temp_dict)
        return jsonify({"status": "true", "message": "user registered", "result": result})

@app.route('/smart_bike/violation', methods=['POST'])
def Violation():
    db = client.smart_bike
    data = mongo.db.smart_bike_users
    coll = db.smart_bike_users_violation
    output = []
    try:
        user_id =int(request.json['user_id'])
        violation = request.json['violation']
        # upload_image = request.json['upload_image']
        # upload_image = upload_image.encode()
        # upload_image_path = '/var/www/html/smartbike/Images/' + 'report' + str(user_id) + '.jpg'
        # mongo_db_upload_image_path = "/smartbike/Images/"  + 'report' + str(user_id) + '.jpg'
        # with open(upload_image_path, 'wb') as f:
        #     f.write(base64.decodebytes(upload_image))
        info = data.find({'user_id': user_id})
        for i in info:
            print(i)
            ik = i['user_id']
            if int(ik) == int(user_id):
                coll.insert({'user_id': user_id, 'violation': violation})
                output.append({'user_id': user_id, 'violation': violation})
                return jsonify({'status': 'success','message':'violation report updated successfully', 'result': output})
            else:
                return jsonify({'status': 'Fail', 'message': 'Data not found'})
        else:
            return jsonify({'status': 'Fail', 'message': 'invalid user_id'})

    except Exception as e:
        return jsonify({'status': 'false', 'result': str(e)})

################################qrcode######################
@app.route('/smart_bike/qrcode', methods=['POST'])
def qr_code():
    db = client.smart_bike
    coll1 = db.smart_bike_qrcode
    user_id = request.json['user_id']
    coll = db.smart_bike_users
    details = coll.find()
    print(details)

    output = []

    for i in details:
        id = i['user_id']
        name = i['user_name']
        if int(id) == int(user_id):
            i = str(id)
            i = i.encode()
            qrcode = pyqrcode.create(i)
            qrcode.png("/var/www/html/smartbike/Images/" + name + '.png', scale=8)

            qr_code = base64.b64encode(open("/var/www/html/smartbike/Images/" + name + '.png', "rb").read())
            print(qr_code)
            image_path = '/var/www/html/smartbike/Images/'+ name + '.png'
            # mongo_db_path = "/var/www/html/smartbike/Images" + name + '.png'
            mongo_db_path = "/smartbike/Images/" + str(name) + '.' + 'jpg'
            # mongo_db_path = "Images" + name + '.png'
            with open(image_path, "wb") as fh:
                fh.write(base64.decodebytes(qr_code))
            coll1.insert({'user_id': user_id, 'qr_code': mongo_db_path})
            output.append({'user_id': user_id, 'qr_code': mongo_db_path})
            print(output)
            return jsonify({'status': 'true', 'result': output})


################################### profile-pic upload ##################################
@app.route('/smart_bike/upload_profile', methods=['POST', 'GET'])
def upload_profile():
    db = client.smart_bike
    coll = db.smart_bike_users
    # print(coll)
    output = []
    try:
        user_id = int(request.json['user_id'])
        upload_img = request.json['upload_img']
        print(type(upload_img))
        if str(upload_img) != "":

         upload_img = upload_img.encode()
        # upload_img_path = "/var/www/html/smartbike/Images/" + str(user_id) + '.jpg'
        # print(upload_pic_path)
         upload_profilepic_path = '/var/www/html/smartbike/Images/' + 'profilepics' + str(user_id) + '.jpg'
         mongo_db_upload_profilepic_path = "/smartbike/Images/" + 'profilepics' + str(user_id) + '.jpg'
        # print(front_image_path)
         with open(upload_profilepic_path, 'wb') as f:
            f.write(base64.decodebytes(upload_img))
            # print(front_image)
         data = coll.find({'user_id': user_id})
         for d in data:
            id = d['user_id']
            # print(id)
            if int(id) == int(user_id):
                if upload_img is not None or upload_img != "":
                # print(d['user_id'])
                 coll.find_one_and_update({'user_id': user_id},
                                         {'$set': {'upload_profilepic_path': mongo_db_upload_profilepic_path}})
                 output.append({'user_id': user_id, 'upload_profilepic_path': mongo_db_upload_profilepic_path})
                return jsonify({'result': output, 'status': 'success', 'message': 'upload profile success'})
            else:
                return jsonify({'result': 'user not found', 'status': 'fail'})
        # return "Unable to upload file. Please try again"
        else:
            return jsonify({'status': 'fail', 'result': 'data not found. please try again'})
    except Exception as e:
        return jsonify({'status': 'fail', 'result': str(e)})


########################################## profile-edit ###########
@app.route('/smart_bike/edit_profile', methods=['POST', 'GET'])
def edit_profile():
    db = client.smart_bike
    coll = db.smart_bike_users
    # print(coll)
    output = []
    try:
        user_id = int(request.json['user_id'])
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        mobile_number = request.json['mobile_number']
        email_id = request.json['email_id']
        address = request.json['address']
        st = randint(1000, 9999)
        upload_img = request.json['upload_img']
        upload_img = upload_img.encode()
        # try:
        #     upload_img = request.json['upload_img']
        # except KeyError:
        #     upload_img = ""
        # upload_img_path = "/var/www/html/smartbike/Images/" + str(user_id) + '.jpg'
        upload_profilepic_path = "/var/www/html/smartbike/Images/" + 'profilepics' + str(user_id)+ str(st) + '.jpg'
        mongo_db_upload_profilepic_path = "/smartbike/Images/" + 'profilepics' + str(user_id) + str(st) + '.jpg'
        # print(upload_pic_path)
        # print(front_image_path)
        with open(upload_profilepic_path, 'wb') as f:
            f.write(base64.decodebytes(upload_img))
            # print(front_image)
        data = coll.find({'user_id': user_id})
        for d in data:
            id = d['user_id']
            print(id)
            if int(id) == int(user_id):
                if upload_img is not None:
                # print(d['user_id'])
                 coll.find_one_and_update({'user_id': user_id},
                                         {'$set': {'upload_profilepic_path': mongo_db_upload_profilepic_path, 'address': address,
                                                   'mobile_number': mobile_number, 'first_name': first_name,
                                                   'last_name': last_name, 'email_id': email_id}})
                 output.append({'user_id': user_id, 'upload_profilepic_path': mongo_db_upload_profilepic_path, 'address': address,
                               'mobile_number': mobile_number, 'first_name': first_name,
                               'last_name': last_name, 'email_id': email_id})
                return jsonify({'result': output, 'status': 'success', 'message': 'edit profile success'})
            else:
                return jsonify({'result': 'user not found', 'status': 'fail'})
        else:
            return jsonify({'status': 'fail', 'result': 'data not found. please try again'})
    except Exception as e:
        return jsonify({'status': 'fail', 'result': str(e)})


##########################getting the details of user################
@app.route('/smart_bike/get_user_info/<user_id>', methods=['POST', 'GET'])
def get_user_info(user_id):
    db = client.smart_bike
    coll = db.smart_bike_users
    output = []
    # user_id= request.json['user_id']
    info = coll.find()
    for i in info:
        user = i['user_id']
        if user == int(user_id):
            user_name = i['user_name']
            mobile_number = i['mobile_number']
            email_id = i['email_id']
            first_name = i['first_name']
            last_name = i['last_name']
            try:
                upload_profilepic_path = i['upload_profilepic_path']

            except KeyError or ValueError:
                upload_profilepic_path = ""
            try:
                address = i['address']


            except KeyError or ValueError:
                address = ""

            output.append(
                {'user_id': user, 'user_name': user_name, 'mobile_number': mobile_number,'email_id':email_id, 'upload_profilepic_path': upload_profilepic_path,'first_name': first_name, 'last_name': last_name,'address':address})
            return jsonify({'status': 'success','message':'user details', 'result': output})
    else:
        return jsonify({'status': 'fail', 'result': 'Unable to retrieve user details, Please try again'})


################################### locations of city's #######################################
@app.route('/smartbike/city_addresses', methods=['GET'])
def city_address():
    db = client.smartbike_admin
    coll = db.smartbike_loc_address
    output = []
    for i in coll.find():
        address = i['address']
        # print(address)
        # exit()
        # latitude = i['latitude']
        # longitude = i['longitude']
        output.append({'address': address})
    return jsonify({'status': 'success', 'result': output})
############################ station_id get bike_details ####################
@app.route('/smartbike/get_station_details/<station_number>', methods=['GET'])
def search(station_number):
     try:
        db = client.smartbike_admin
        data = db.smartbike_bike_details
        # print(data)
        # station_name = request.json['station_name']
        # station_id = str(request.json['station_id'])
        output = []
        bike_count = []
        for i in data.find({'station_number':int(station_number)}):
            id = i['station_number']
            # id = i['station_id']

            if int(id) == int(station_number):
                bike_id = i['bike_id']
                bike_count.append(bike_id)

                output.append({'station_number':id,'bike_frame_number':i['bike_frame_number'],'latitude':i['latitude'],'longitude':i['longitude'],'bike_type':i['bike_type']})

        # output.append(bike_count)
        return jsonify({'status': 'success', 'message': 'list of bikes in a station','bike_count':len(bike_count) ,'result': output})
     except Exception as e:
         return jsonify(status="Fail", message=str(e))
#######################################get stations #################################3
@app.route('/smartbike/get_station_bike/', methods=['GET'])
def smart_search():
     try:
        db = client.smartbike_admin
        data = db.smartbike_bike_details
        # print(data)
        # station_name = request.json['station_name']
        # station_id = str(request.json['station_id'])
        output = []
        bike_count = []
        for i in data.find():
            name = i['station_name']
            id = i['station_number']




            output.append({'station_number':i['station_number'],'station_name':name,'country':i['country'],'city_name':i['city_name'],'latitude':i['latitude'],'longitude':i['longitude']})

        return jsonify({'status': 'success', 'message': 'list of bikes in a station' ,'result':output})
     except Exception as e:
         return jsonify(status="Fail", message=str(e))
#########################user_feed back################################

@app.route('/smartbike/rating_feedback', methods=['POST'])
def feedback():
    db = client.smart_bike
    coll = db.smart_bike_users
    # data = mongo.db.Registe
    output=[]
    user_id = int(request.json['user_id'])
    rating = float(request.json['rating'])
    comment = request.json['comment']
    # note = request.json['note']
    coll.find_one_and_update({'user_id': user_id}, {'$set': {'rating': rating, 'comment':comment }})
    output.append({'user_id': user_id, 'rating': rating, 'comment': comment})
    return jsonify({'status': 'success', 'message': 'Rating Feedback added successfully','result':output})

##################terms&conditions##################################

@app.route('/smart_bike/about', methods=['POST', 'GET'])
def smartbike():
    data = client.smartbike_admin
    coll = data.smartbike_abouts

    type = request.json['type']
    if type == "AboutUs":
        details = coll.find_one({"Type": type})
        output = []
        output_dict = {'type': type, 'path': details['Path']}
        output.append(output_dict)
        if details['Path'] != 0:
            return jsonify({"status": "success", "message": "AboutUs document", "result": output})
        else:
            return jsonify({"status": "failure", "message": "AboutUs data not get it."})
    elif type == "TermsandConditions":
        details = coll.find_one({"Type": type})
        output = []
        output_dict = {'type': type, 'path': details['Path']}
        output.append(output_dict)
        if details['Path'] != 0:
            return jsonify({"status": "success", "message": "Terms and Condition document", "result": output})
        else:
            return jsonify({"status": "failure", "message": "Did not get Terms&Condition document"})
    elif type == "PrivacyPolicy":
        details = coll.find_one({"Type": type})
        output = []
        output_dict = {'type': type, 'path': details['Path']}
        output.append(output_dict)
        if details['Path'] != 0:
            return jsonify({"status": "success", "message": "privacy_policy document", "result": output})
        else:
            return jsonify({"status": "failure", "message": "Did not get privacy_policy document"})
    elif type == "FAQ":
        details = coll.find_one({"Type": type})
        output = []
        output_dict = {'type': type, 'path': details['Path']}
        output.append(output_dict)
        if details['Path'] != 0:
            return jsonify({"status": "success", "message": "FAQ document", "result": output})
        else:
            return jsonify({"status": "failure", "message": "Did not get FAQ document"})
    else:
        return jsonify({"status": "failure", "message": "Didn't get any data"})

#################################getting the files##############################
@app.route('/smart_bike/aboutus_files/<Id>', methods=['GET'])
def get_aboutus(Id):
    # data = mongo.db.About_Fitzcube
    data = client.smartbike_admin
    coll = data.smartbike_abouts
    output = []
    details = coll.find()
    print(details)

    for q in details:
        id = q['Id']
        # print(id)
        # type = q['Type']
        # print(type)
        if int(id) == int(Id):
            # for s in q:
                output.append({'id': q['Id'], 'type': q['Type'], 'file_path': q['Path']})
                return jsonify({'status': 'success', 'message': 'About smartbike data get successfully','result': output})


#######################get location based on bike count
@app.route('/smart_bike/get_loc_address', methods=['POST', 'GET'])
def get_loc_address():
    try:
        data = client.smartbike_admin
        coll = data.smartbike_loc_address
        #coll1=data.bike_details
        #station_id=request.json['station_id']

        output=[]

        for j in coll.find():
           # coll.update({'station_id':station_id},{'$set':{'latitude':j['latitude'],'longitude':j['longitude'],'station_name':j['station_name'],'station_id':j['station_id']}})
            output.append({'latitude':j['latitude'],'longitude':j['longitude'],'station_name':j['station_name'],'station_number':j['station_number'],'bike_count':j['bike_count']})


        return jsonify({'status': 'success', 'message': 'event dates get successfully', 'result': output})

    except Exception as e:
            return jsonify(status="fail", message=str(e))


###################################bike_number###################################
@app.route('/smartbike/bike_avalibility_details/<bike_frame_number>', methods=['GET','POST'])
def details32(bike_frame_number):
    data = client.smartbike_admin
    coll = data.smartbike_bike_details
    output = []
    Bike_status=True
    bike_booking_status=request.json['bike_booking_status']
    min = 3
        # min = min - 1
        # time.sleep(1)
    count_down_time = min

    for i in coll.find():
            id = i['bike_frame_number']

            coll.update({"bike_frame_number":id},{'$set':{'bike_booking_status':bike_booking_status}})

            output.append({"bike_frame_number": i['bike_frame_number'], 'count_down_time':count_down_time, 'Bike_status':'Available', "bike_lock_type": i['bike_lock_type'],"bike_lock_number":i['bike_lock_number'],"bike_type":i['bike_type'],"bike_id":i['bike_id'],
                                 'bike_booking_status':bool(bike_booking_status)})
            return jsonify({"status": "success", "message": " data get successfully", "result": output})
    else:
            return jsonify({"status": "fail", "message": "please try again or user is not in database", "bike_frame_number": bike_frame_number})


# ###################################bike_lock_details###################################
# @app.route('/smartbike/bike_lock_details/<bike_frame_number>', methods=['GET'])
# def details321(bike_frame_number):
#     data = client.smartbike_admin
#     coll = data.bike_details
#     output = []
#     Bike_status=Truedit
#     # count_down_time = '1 min'
#     try:
#         for i in coll.find():
#             id = i['bike_frame_number']
#             count_down_time = '1 min'
#             if int(id) == int(bike_frame_number):
#                 if ( Bike_status== True):
#
#                     output.append({ 'count_down_time':count_down_time, 'Bike_status':'Available', "bike_lock_number":i['bike_lock_number']
#                                  })
#                     return jsonify({"status": "success", "message": "data get successfully", "result": output})
#         else:
#             return jsonify({"status": "fail", "message": "please try again or user is not in database", "bike_frame_number": bike_frame_number})
#
#     except Exception as e:
#         return jsonify(status="fail", message=str(e))
#


##############################report a problem#########################
# @app.route('/smart_bike/reportproblem', methods=['POST'])
# def reportproblem():
#     db = client.smart_bike
#     coll = db.smart_bike_reportproblem
#     output = []
#     try:
#         user_id = int(request.json['user_id'])
#         try:
#             reason = request.json['reason']
#         except KeyError or ValueError:
#             reason = ""
#         try:
#             attach_photo = request.json['attach_photo']
#             attach_photo = attach_photo.encode()
#         except KeyError or ValueError:
#             attach_photo = ""
#         upload_attach_photo_path = '/var/www/html/smartbike/Images/' + 'reportproblem' + str(user_id) + '.jpg'
#             # upload_image_path = '/var/www/html/smartbike/Images' + str(user_id) + '.jpg'
#
#         mongo_db_attach_photo_path = "/smartbike/Images/"  + 'reportproblem' + str(user_id) + '.jpg'
#         with open(upload_attach_photo_path, 'wb') as f:
#                 f.write(base64.decodebytes(attach_photo))
#
#         coll.insert({'user_id': user_id,'reason': reason,'upload_attach_photo_path': mongo_db_attach_photo_path})
#         output.append({'user_id': user_id, 'reason': reason,
#                            'upload_attach_photo_path': mongo_db_attach_photo_path})
#         return jsonify({'status': 'true', 'result': output})
#     except Exception as e:
#         return jsonify({'status': 'false', 'result': str(e)})

@app.route('/smart_bike/reportproblem/<user_id>', methods=['POST'])
def reporting(user_id,attach_image=None):
    db = client.smart_bike
    data = mongo.db.smart_bike_users

    coll = db.smart_bike_problem
    output = []
    photo=[]
    try:
        # user_id = request.json['user_id']

        reason = request.json['reason']
        try:
            attach_image = request.json['attach_image']
        except KeyError:
            attach_image = None

        if attach_image is None:
                print('here photo is not attached')

        else:
            attach_image = attach_image.encode()
            attach_image_path = '/var/www/html/smartbike/Images/' + 'report' + str(user_id) + '.jpg'
            mongo_db_upload_image_path = "/smartbike/Images/" + 'report' + str(user_id) + '.jpg'
            with open(attach_image_path, 'wb') as f:
                f.write(base64.decodebytes(attach_image))
                photo.append(mongo_db_upload_image_path)

        coll.insert({'user_id': int(user_id), 'reason': reason, 'upload_image_path': photo})
        # db.removeEmptyFieldsDemo.insertOne({"StudentName": ""})
        output.append({'user_id': user_id, 'reason': reason,
                       'upload_image_path': photo})
        return jsonify({'status': "success",'message': 'your problem reported successfully',  'result': output})
        # return jsonify({'status': "success", 'result': output})
            # else:
            #     return jsonify({'status': 'Fail', 'message': 'Data not found'})
        # else:
        #     return jsonify({'status': 'Fail', 'message': 'invalid user_id'})

    except Exception as e:
        return jsonify({'status': 'false', 'result': str(e)})




##################################report_problem_delete################################
@app.route('/smart_bike/delete_problem', methods=['POST', 'GET'])
def delete_problem():
    try:
        db = client.smart_bike
        coll = db.smart_bike_reportproblem
        user_id = int(request.json['user_id'])

        for q in coll.find({'user_id': user_id}):
            coll.remove({'user_id': user_id})

        return jsonify({'status': 'deleted  successfully'})

    except Exception as e:
        return jsonify(status="fail", message=str(e))





########################################## report a problem edit ###########
################################ report-edit ############################################
@app.route('/smart_bike/edit_reportproblems', methods=['POST', 'GET'])
def edit_report32():
    db = client.smart_bike
    coll1 = db.smart_bike_reportproblem
    coll2 = db.smart_bike_users
    # print(coll)
    output = []
    try:
        user_id = int(request.json['user_id'])
        reason=request.json['reason']

        try:
            attach_photo = request.json['attach_photo']
            attach_photo = attach_photo.encode()
        except KeyError or ValueError:
            attach_photo = ""
        upload_attach_photo_path = '/var/www/html/smartbike/Images/' + 'reportproblem'+str(user_id)+'.jpg'
        mongo_db_attach_photo_path = "/smartbike/Images/" + 'reportproblem' + str(user_id) + '.jpg'
        # back_image_mongo_db_path = '/Images/' + str(user_id) + '.' + 'jpg'
        with open(upload_attach_photo_path, 'wb') as f:
            f.write(base64.decodebytes(attach_photo))
        data = coll2.find()
        for d in data:
            id = d['user_id']
            # print(id)
            if int(id) == int(user_id):
                    coll1.update({'user_id': user_id}, {
                        '$set': {'reason': reason, 'upload_attach_photo_path': mongo_db_attach_photo_path}})

                    output.append(
                        {'user_id': user_id, 'reason': reason, 'upload_attach_photo_path': mongo_db_attach_photo_path})
                    return jsonify({'result': output, 'status': 'true', 'message': 'user edited details successfully'})
        else:
            return jsonify({"status": "fail", 'message': 'please try again.....!'})
    except Exception as e:
        return jsonify({'status':'Fail','message':'Invalid UserId'})


###########################getting all report problems #########################
@app.route('/smart_bike/problemsofuser', methods=['GET'])
def reports():
    db = client.smart_bike
    coll = db.smart_bike_reportproblem
    output =[]
    # user_id = request.json['user_id']
    for q in coll.find():
        output.append({'user_id':q['user_id'],'reason':q['reason'],'upload_attach_photo_path':q['upload_attach_photo_path']})
    return jsonify({'status': 'success', 'message': 'Data get sucessfully', 'result': output})



#####################################damaged vechicle############################
@app.route('/smartbike/Damaged_vehicle', methods=['POST'])
def damaged_vehicle():
    db = client.smart_bike
    coll = db.smart_bike_damagedvehicle
    # db=mongo.db.register
    # data = mongo.db.damaged_vehicle
    output = []
    try:
        user_id = int(request.json['user_id'])
        try:
            damaged_part  = request.json['damaged_part']
        except KeyError or ValueError:
            damaged_part = ""

        coll.insert({'user_id':user_id,'damaged_part':damaged_part})
        output.append({'user_id':user_id,'damaged_part':damaged_part})
        return jsonify({'status': 'success', 'message': 'selected parts of the vehicle updated successfully', 'result': output})

    except Exception as e:
        return jsonify({'status':'Fail', 'message':'Invalid UserId'})

@app.route('/smart_bike/edit_Damaged_vehicle', methods=['POST'])
def edit_Damaged_vehicle():
    db = client.smart_bike
    coll = db.smart_bike_damagedvehicle
    output = []
    try:
        user_id = request.json['user_id']
        try:
            damaged_part = request.json['damaged_part']
        except KeyError or ValueError:
            damaged_part =""

        info = coll.find({'user_id':user_id})
        for i in info:
            print(i)
            ik = i['user_id']

            if int(ik) == int(user_id):
                coll.find_one_and_update({'user_id':user_id},{'$set':{'damaged_part':damaged_part,}})
                output.append({'user_id':user_id,'damaged_part':damaged_part})
                return jsonify({'status':'success','message':'Damaged vehicle data edited successfully'})

    except Exception as e:
        return jsonify({'status':'Fail','message':'Invalid UserId'})

################################delete damaged part################################
@app.route('/smart_bike/delete_damaged_part', methods=['POST', 'GET'])
def delete_damagedpart():
    try:
        db = client.smart_bike
        coll = db.smart_bike_damagedvehicle
        user_id = int(request.json['user_id'])

        for q in coll.find({'user_id': user_id}):
            coll.remove({'user_id': user_id})

        return jsonify({'status': 'deleted  successfully'})

    except Exception as e:
        return jsonify(status="fail", message=str(e))


###########################getting damaged vechicle parts based on user_id#########################
@app.route('/smart_bike/get_Damaged_vehicle', methods=['GET'])
def get_damaged_vehicle1():
    db = client.smart_bike
    coll = db.smart_bike_damagedvehicle
    output =[]
    user_id = request.json['user_id']
    for q in coll.find({'user_id':user_id}):
        output.append({'user_id':q['user_id'],'damaged_part':q['damaged_part']})
        return jsonify({'status': 'success', 'message': 'Data get sucessfully', 'result': output})
    return jsonify({'status': 'success', 'message': 'Data get sucessfully', 'result': output})

################################bike_count##################################
@app.route('/smart_bike/bike_count', methods=['POST', 'GET'])
def loc_address():
    # try:
        data = client.smartbike_admin
        coll1=data.smartbike_bike_details
        # coll2 = data.smartbike_jhansi
        output=[]
        cursor=coll1.aggregate([{
            '$group': {
                '_id': '$station_number',
                'station_number': { '$first': '_id'},
                # 'bike_id':{'$first':'$bike_id'},
                'station_name':{'$first':'$station_name'},
                'latitude': {'$first': '$latitude'},
                'longitude':{'$first':'$longitude'},
                 'bike_racks':{'$first':'$bike_racks'},

            'count': { '$sum': 1}
            }
            }])

        # for j in coll2.find():

        for i in cursor:
                 output.append({'station_number':i['_id'],'station_name':i['station_name'],'latitude':i['latitude'],'longitude':i['longitude'],'bike_count':i['count'],'bike_racks':i['bike_racks']})
        return jsonify({'status': 'success', 'message': 'station details getting successfully', 'result': output})


##########################getting the kyc details of user through registration################
@app.route('/smart_bike/get_kyc_details_user/<user_id>', methods=['POST', 'GET'])
def kyc_details_user(user_id):
    db = client.smart_bike
    coll = db.smart_bike_users
    output = []
    kyc_status=True
    # user_id= request.json['user_id']
    info = coll.find()
    for i in info:
        user = i['user_id']
        if user == int(user_id):
            if(kyc_status==True):

                    try:
                        user_name = i['user_name']
                    except KeyError or ValueError:
                        user_name = ""
                    try:
                        date_of_upload = i['date_of_upload']
                    except KeyError or ValueError:
                        date_of_upload = ""


                    try:
                        id_proof = i['id_proof']
                    except KeyError or ValueError:
                        id_proof = ""

                    try:
                        id_proof_num = i['id_proof_num']
                    except KeyError or ValueError:
                        id_proof_num = ""
                    try:
                        front_image = i['front_image_path']
                    except KeyError or ValueError:
                        front_image = ""
                    try:
                        back_image = i['back_image_path']
                    except KeyError or ValueError:
                        back_image = ""

                    output.append(
                        {'user_id': user, 'user_name': user_name, 'front_image': front_image, 'back_image': back_image,
                         'date_of_upload': date_of_upload,
                         'kyc_status': i['kyc_status'], 'id_proof': id_proof,'id_proof_num':id_proof_num})
                    return jsonify({'status': 'success', 'message':'this is your kyc details','result': output})
            else:
                return jsonify({'status': 'fail', 'result': 'Unable to retrieve user details, Please try again'})


############################################# Get Offer_management ######################################
@app.route('/smart_bike/get_offer_management_voucher_code', methods=['GET','POST'])
def get_offer_management22():
    data = client.smartbike_admin
    coll = data.smartbike_offer_management
    # voucher_code=request.json['voucher_code']
    output = []
    for i in coll.find():
        voucher_code2= i['voucher_code']
        output.append({'voucher_code': voucher_code2})
    return jsonify({'status': 'success', 'result': output,'message':'offer details'})

###################
@app.route('/smart_bike/get_offer_management', methods=['GET','POST'])
def get_offer_management():
    data = client.smartbike_admin
    coll = data.smartbike_offer_management
    db = client.smart_bike
    coll1 = db.smart_bike_apply_promocode
    voucher_code=request.json['voucher_code']
    output = []
    for i in coll.find():
        id = i['voucher_code']
        if id == voucher_code:
           coll1.insert({'voucher_code':voucher_code})
           output.append({'start_date': i['start_date'],'voucher_name': i['voucher_name'],
                       'end_date': i['end_date'], 'cash_bonus':i['cash_bonus']})
    return jsonify({'status': 'success', 'result': output,'message':'offer details'})





############################### tariff-edit ############################################
@app.route('/smart_bike/tariff', methods=['POST', 'GET'])
def tariff():
    db = client.smart_bike
    coll = db.smart_bike_users
    # print(coll)
    output = []
    tariff_plan =bool(request.json['tariff_plan'])
    user_id = int(request.json['user_id'])
    subscription_plan = request.json['subscription_plan']
    Current_Date = datetime.datetime.today()
    data = coll.find()
    for d in data:
        id = d['user_id']
        # print(id)
        if int(id) == int(user_id):
            # print(d['user_id'])

            if (subscription_plan == 'OneDay_Pass'):
                # Current_Date = datetime.datetime.today()
                NextDay_Date = Current_Date
                NextDay_Date_out = NextDay_Date + datetime.timedelta(days=1)
                if(NextDay_Date):
                    coll.update({'user_id': user_id}, {
                        '$set': {'subscription_plan':subscription_plan,'member_price':49,'tariff_plan': tariff_plan,'valid_upto':NextDay_Date,'date_of_subscribed':Current_Date}})
                    output.append(
                        {'user_id': user_id, 'subscription_plan':subscription_plan,'member_price':49 ,'tariff_plan': tariff_plan,
                         'date_of_subscribed': Current_Date,'valid_upto':NextDay_Date
                         })
                    return jsonify({'result': output, 'status': 'active', 'message': 'your are in weekly subscription plan'})
                elif(NextDay_Date_out):
                    coll.update({'user_id': int(user_id)},
                                {'$unset': {'subscription_plan': 1, 'member_price': 1, 'tariff_plan': 1, 'date_of_subscribed': 1,'valid_upto':1
                                        }})
                    coll.find_one_and_update({'user_id': int(user_id)}, {'$set':{'tariff_plan': False}})
                    return jsonify({ 'status': 'inactive', 'message': 'your subscription_plan is expired '})
                else:
                    return jsonify({"status": "fail", 'message': 'please try again.....!'})

            elif (subscription_plan == 'Weekly_Pass'):
                # Current_Date = datetime.datetime.today()
                NextDay_Date = Current_Date + datetime.timedelta(days=7)
                NextDay_Date_out = NextDay_Date + datetime.timedelta(days=1)
                if(NextDay_Date):

                    coll.update({'user_id': user_id}, {
                        '$set': {'subscription_plan':subscription_plan,'member_price':199,'tariff_plan': tariff_plan,'valid_upto':NextDay_Date,'date_of_subscribed':Current_Date}})
                    output.append(
                        {'user_id': user_id, 'subscription_plan':subscription_plan,'member_price':199 ,'tariff_plan': tariff_plan,
                         'date_of_subscribed': Current_Date,'valid_upto':NextDay_Date
                         })
                    return jsonify({'result': output, 'status': 'active', 'message': 'your are in weekly subscription plan'})
                elif(NextDay_Date_out):
                    coll.update({'user_id': int(user_id)},
                                {'$unset': {'subscription_plan': 1, 'member_price': 1, 'tariff_plan': 1, 'date_of_subscribed': 1,'valid_upto':1
                                        }})
                    coll.find_one_and_update({'user_id': int(user_id)}, {'$set': {'tariff_plan': False}})
                    return jsonify({ 'status': 'inactive', 'message': 'your subscription_plan is expired '})
                else:
                    return jsonify({"status": "fail", 'message': 'please try again.....!'})

            elif (subscription_plan == 'Monthly_Pass'):
                NextDay_Date =Current_Date + datetime.timedelta(days=30)
                NextDay_Date_out = NextDay_Date+ datetime.timedelta(days=1)
                if (NextDay_Date):
                    coll.update({'user_id': user_id}, {
                        '$set': {'subscription_plan': subscription_plan, 'member_price': 399,
                                 'tariff_plan': tariff_plan, 'valid_upto': NextDay_Date,'date_of_subscribed':Current_Date}})

                    output.append(
                        {'user_id': user_id, 'subscription_plan': subscription_plan, 'member_price': 399,
                         'tariff_plan': tariff_plan,
                         'date_of_subscribed': Current_Date, 'valid_upto': NextDay_Date
                         })
                    return jsonify({'result': output, 'status': 'active', 'message': 'your are in Monthly_Pass subscription plan'})
                elif (NextDay_Date_out):
                    coll.update({'user_id': int(user_id)},
                                {'$unset': {'subscription_plan': 1, 'member_price': 1, 'tariff_plan': 1,
                                            'date_of_subscribed': 1, 'valid_upto': 1
                                            }})
                    coll.find_one_and_update({'user_id': int(user_id)}, {'$set': {'tariff_plan': False}})
                    return jsonify(
                        {'status': 'inactive', 'message': 'your subscription_plan is expired '})
                else:
                    return jsonify({"status": "fail", 'message': 'please try again.....!'})

            elif (subscription_plan == '3_Monthly_Pass'):
                NextDay_Date = Current_Date + datetime.timedelta(days=90)
                NextDay_Date_out = NextDay_Date + datetime.timedelta(days=1)
                if (NextDay_Date):
                    coll.update({'user_id': user_id}, {
                        '$set': {'subscription_plan': subscription_plan, 'member_price': 599,
                                 'tariff_plan': tariff_plan, 'valid_upto': NextDay_Date,
                                 'date_of_subscribed': Current_Date}})

                    output.append(
                        {'user_id': user_id, 'subscription_plan': subscription_plan, 'member_price': 599,
                         'tariff_plan': tariff_plan,
                         'date_of_subscribed': Current_Date, 'valid_upto': NextDay_Date
                         })
                    return jsonify(
                        {'result': output, 'status': 'active', 'message': 'your are in 3_Monthly_Pass subscription plan'})
                elif (NextDay_Date_out):
                    coll.update({'user_id': int(user_id)},
                                {'$unset': {'subscription_plan': 1, 'member_price': 1, 'tariff_plan': 1,
                                            'date_of_subscribed': 1, 'valid_upto': 1
                                            }})
                    coll.find_one_and_update({'user_id': int(user_id)}, {'$set': {'tariff_plan': False}})
                    return jsonify(
                        {'status': 'inactive', 'message': 'your subscription_plan is expired '})
                else:
                    return jsonify({"status": "fail", 'message': 'please try again.....!'})

            elif (subscription_plan == 'Yearly_Pass'):
                NextDay_Date = Current_Date+ datetime.timedelta(days=365)
                NextDay_Date_out =NextDay_Date + datetime.timedelta(days=1)
                if (NextDay_Date):
                    coll.update({'user_id': user_id}, {
                        '$set': {'subscription_plan': subscription_plan, 'member_price': 1999,
                                 'tariff_plan': tariff_plan, 'valid_upto': NextDay_Date,'date_of_subscribed':Current_Date}})
                    output.append(
                        {'user_id': user_id, 'subscription_plan': subscription_plan, 'member_price': 1999,
                         'tariff_plan': tariff_plan,
                         'date_of_subscribed': Current_Date, 'valid_upto': NextDay_Date
                         })
                    return jsonify(
                        {'result': output, 'status': 'active',
                         'message': 'your are in Yearly_Pass subscription plan'})
                elif (NextDay_Date_out):
                    coll.update({'user_id': int(user_id)},
                                {'$unset': {'subscription_plan': 1, 'member_price': 1, 'tariff_plan': 1,
                                            'date_of_subscribed': 1, 'valid_upto': 1
                                            }})
                    coll.find_one_and_update({'user_id': int(user_id)}, {'$set': {'tariff_plan': False}})
                    return jsonify(
                        {'status': 'inactive', 'message': 'your subscription_plan is expired '})
                else:
                    return jsonify({"status": "fail", 'message': 'please try again.....!'})
            else:
                return jsonify({"status": "fail", 'message': 'please try again.....!'})

    else:
        return jsonify({"status": "fail", 'message': 'please try again.....!'})


################################ tariff_plan expired ###########################
@app.route('/smart_bike/tariff_plan_expired', methods=['POST', 'GET'])
def tariff_plan_expired():
    db = client.smart_bike
    coll = db.smart_bike_users
    user_id = request.json['user_id']
    try:
        data = coll.find()
        for d in data:
            id = d['user_id']
            if str(id) == str(user_id):
                 coll.update({'user_id': int(user_id)},
                                {'$unset': {'subscription_plan': 1, 'member_price': 1, 'tariff_plan': 1,
                                            'date_of_subscribed': 1, 'valid_upto': 1}})
                 coll.find_one_and_update({'user_id': int(user_id)}, {'$set': {'tariff_plan': False}})
                 return jsonify(
                        {'status': 'inactive', 'message': 'your subscription_plan is expired '})
    except Exception as e:
        return jsonify({'status': 'fail', 'result': str(e)})

###########################get_kyc#####################################
@app.route('/smart_bike/customer_details/tariff_planstatus/is_true', methods=['GET'])
def customer_tariff_plan_details():
    db = client.smart_bike
    coll = db.smart_bike_users
    output_list = []
    details = coll.find()
    for u_id in details:  # here u_id is the iteration variable to check the all users in database
        ks = u_id['tariff_plan']
        # print(ks)
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
            # temp_dict['tariff_plan'] = u_id['tariff_plan']
            try:
                temp_dict['login_type'] = u_id['login_type']
            except KeyError or ValueError:
                temp_dict['login_type'] = ""
            try:
                temp_dict['tariff_plan'] = u_id['tariff_plan']
            except KeyError or ValueError:
                temp_dict['tariff_plan'] = ""

            output_list.append(temp_dict)

    return jsonify({"status": "success", "message": "success", "result": output_list})


###################
@app.route('/smart_bike/tariff_management', methods=['GET','POST'])
def tariff_management():
    data = client.smartbike_admin
    coll = data.smartbike_tariff_management
    try:

        city_name=request.json['city_name']
        city_id = int(request.json['city_id'])
        subscripition_plan = request.json['subscripition_plan']
        member_price=int(request.json['member_price'])
        output = []
        # subscripition_id_list = [i['subscripition_id'] for i in coll.find()]
        # if len(subscripition_id_list) is 0:
        #     subscripition_id = 1
        # else:
        #     subscripition_id = int(subscripition_id_list[-1]) + 1
        coll.insert({'city_name':city_name,'city_id':city_id,'subscripition_plan':subscripition_plan,'member_price':member_price,'subscripition_id':subscripition_id})
        output.append({'city_name':city_name,'city_id':city_id,'subscripition_plan':subscripition_plan,'member_price':member_price,'subscripition_id':subscripition_id})
        return jsonify({'status': 'success', 'result': output,'message':'tariff details'})
    except Exception as e:
            return jsonify({'status': 'fail', 'result': str(e)})


######################################## logout ################################
@app.route('/smart_bike/logout', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
@login_required
def logout():
    session.clear()
    flask_login.logout_user()
    return redirect(url_for('/smart_bike/login'))
# @app.route('/moaisys/resumes', methods=['POST'])
# def get_resumes():
#     data = client.smartbike_admin
#     coll = data.moaisys_resumes
#     user_id = request.json['user_id']
#     url ="http://103.248.211.205/ats/uat/api/resumes?user_id=" +  user_id
#     f = requests.get(url).json()
#
#
#     return jsonify({'f':f})


if __name__ == '__main__':
    #app.run(debug= True)
    app.run(host='0.0.0.0', port=6001, debug=True, threaded=True)

