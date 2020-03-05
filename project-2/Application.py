from flask import Flask,request,jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from time import strftime
from random import randint
import base64,re

app = Flask(__name__)
app.config["MONGO_DBNAME"] = "fitzcube"
# app.config["MONGO_URI"] = "mongodb://3.105.128.235:6909/fitzcube"
app.config["MONGO_URI"] = "mongodb://localhost:27017/fitzcube"
mongo = PyMongo(app)
CORS(app)

#######################################Registration#############################
@app.route('/fitzcube/Register',methods=['POST'])
def register():
    try:
        data = mongo.db.register
        firstname = request.json['firstname']
        lastname = request.json['lastname']
        emailid = request.json['emailid']
        password = request.json['password']
        mobilenumber = request.json['mobilenumber']
        gender = request.json['gender']
        updated_time = strftime("%Y/%m/%d %H:%M:%S %I%p")
        email_result = data.find({'EmailId': emailid})
        mobile_result = data.find({'MobileNumber': mobilenumber})
        user_id_list = [i['UserId'] for i in data.find()]
        if len(user_id_list) is 0:
            user_id = 1
        else:
            user_id = int(user_id_list[-1]) + 1
        if email_result.count()!=0 or mobile_result.count()!= 0:
            return jsonify({'status': 'failure', 'message': 'User is already registered '})
        else:
            if re.fullmatch('^([a-zA-Z]{1,20})$', firstname):#check for first name properly
                if re.fullmatch('^([a-zA-Z]{1,20})$', lastname):#check for last name properly
                    if re.fullmatch('\w[a-zA-Z0-9@_.]*@[a-z0-9]+[.][a-z]+', emailid):#check for emailid properly
                        if re.match(pattern=r'(^(0/91))?([0-9]{10}$)', string=mobilenumber):#check for mobilenumber properly
                            if re.match(r'[A-Za-z0-9@#$%^&+=]{6,12}', password):#check for password properly
                                output = []
                                data.insert({'UserId': int(user_id),'FirstName': firstname,'LastName': lastname,'MobileNumber': mobilenumber,
                                             'EmailId': emailid,'Password': password,'Gender': gender,'UpdatedTime': updated_time})
                                output.append({'user_id':user_id,'firstname':firstname,'lastname':lastname,'mobilenumber':mobilenumber,'emailid':emailid,
                                               'password':password,'gender':gender,'updated_time':updated_time})
                                return jsonify({'status': 'success', 'message': 'User is registered','result':output})
                            else:
                                return jsonify({'status': 'failure', 'message': 'Invalid Password.'})
                        else:
                            return jsonify({'status': 'failure', 'message': 'Invalid Mobile Number'})
                    else:
                        return jsonify({'status': 'failure', 'message': 'Invalid EmailId'})
                else:
                    return jsonify({'status': 'failure', 'message': 'Invalid lastname'})
            else:
                return jsonify({'status': 'failure', 'message': 'Invalid firstname'})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

#############################Send Otp######################################
@app.route('/fitzcube/Reg_OTP', methods=['POST'])
def Reg_OTP():
    try:
        register = mongo.db.register
        mobilenumber = str(request.json['mobilenumber'])
        if register.find_one({'MobileNumber': mobilenumber}) is not None:
            register = mongo.db.register
            otp_value = randint(1000, 9999)
            flag = 0
            if len(mobilenumber) is 10:
                flag = 1
                mobilenumber = "+91" + " " + str(mobilenumber)
            if flag == 1:
                mobilenumber = mobilenumber.split(' ')[1]
            register.find_one_and_update({'MobileNumber': mobilenumber},{'$set':{'OTP': str(otp_value)}})
            return jsonify({'status': "success", "message": "OTP generated successfully","OTP":str(otp_value)})
        else:
            return jsonify({'status': "failure", "message": "MobileNumber entered is not in the Database.Please enter registered mobilenumber!!!"})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

#############################VerifyOTP###########################################
@app.route('/fitzcube/verify_otp',methods=['POST'])
def verify_otp():
    try:
        data = mongo.db.register
        otp_entered = str(request.json['otp_entered'])
        mobilenumber = str(request.json['mobilenumber'])
        output = []
        details = data.find({'MobileNumber': str(mobilenumber),'OTP': str(otp_entered)})
        for j in details:
            output.append({'user_id':j['UserId'],'firstname':j['FirstName'],'lastname':j['LastName'],'emailid':j['EmailId'],'password':j['Password'],
                           'mobilenumber':j['MobileNumber'],'gender':j['Gender'],'otp_entered':j['OTP'],'Verified':1,'updated_time':j['UpdatedTime']})
        finaloutput = {}
        if len(output) != 0:
            finaloutput['status'] = 'success'
            finaloutput['message'] = ' user data get successfully'
            finaloutput['result'] = output
        else:
            finaloutput['status'] = 'failure'
            finaloutput['message'] = 'Invalid Credentials. Please check and try again'
            finaloutput['result'] = []
        return jsonify(finaloutput)
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

#####################ResendOTP#################################################
@app.route('/fitzcube/resend_otp', methods=['POST'])
def resend_otp():
    try:
        register = mongo.db.register
        mobilenumber = str(request.json['mobilenumber'])
        if register.find_one({'MobileNumber': mobilenumber}) is not None:
            register = mongo.db.register
            otp_value = randint(1000, 9999)
            flag = 0
            if len(mobilenumber) is 10:
                flag = 1
                mobilenumber = "+91" + " " + str(mobilenumber)
            if flag == 1:
                mobilenumber = mobilenumber.split(' ')[1]
            register.find_one_and_update({'MobileNumber': mobilenumber},{'$set':{'OTP': str(otp_value)}})
            return jsonify({'status': "success", "message": "OTP generated successfully","OTP":str(otp_value)})
        else:
            return jsonify({'status': "failure", "message": "MobileNumber entered is not in the Database.Please enter registered mobilenumber!!!"})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

##########################################Login###########################################
@app.route('/fitzcube/login',methods=['POST'])
def login():
    try:
        data = mongo.db.register
        username = request.json['username']
        password = request.json['password']
        output = []
        details = data.find({'MobileNumber': username,'Password': password})
        for j in details:
            output.append({'user_id':j['UserId'],'firstname':j['FirstName'],'lastname':j['LastName'],'emailid':j['EmailId'],'password':j['Password'],
                           'mobilenumber':j['MobileNumber'],'gender':j['Gender'],'updated_time':j['UpdatedTime']})
        finaloutput = {}
        if len(output) != 0:
            finaloutput['status'] = 'success'
            finaloutput['message'] = 'login Successfully'
            finaloutput['result'] = output
        else:
            finaloutput['status'] = 'failure'
            finaloutput['message'] = 'Invalid Credentials. Please check and try again'
            finaloutput['result'] = []
        return jsonify(finaloutput)
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

###########################################Forgot Password#####################################
@app.route('/fitzcube/forgot_password', methods=['POST'])
def forgot_password():
    try:
        register = mongo.db.register
        mobilenumber = str(request.json['mobilenumber'])
        if register.find_one({'MobileNumber': mobilenumber}) is not None:
            register = mongo.db.register
            otp_value = randint(1000, 9999)
            flag = 0
            if len(mobilenumber) is 10:
                flag = 1
                mobilenumber = "+91" + " " + str(mobilenumber)
            if flag == 1:
                mobilenumber = mobilenumber.split(' ')[1]
            register.find_one_and_update({'MobileNumber': mobilenumber},{'$set':{'OTP': str(otp_value)}})
            return jsonify({'status': "success", "message": "OTP generated successfully","OTP":str(otp_value)})
        else:
            return jsonify({'status': "failure", "message": "MobileNumber entered is not in the Database.Please enter registered mobilenumber!!!"})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

#############################################change password#####################################
@app.route('/fitzcube/change_password', methods=['POST'])
def change_password():
    try:
        register = mongo.db.register
        password = str(request.json['changed_password'])
        mobile_number = str(request.json['mobilenumber'])
        register.find_one_and_update({'MobileNumber': mobile_number}, {'$set': {'Password': password}})
        return jsonify({'status': 'success', "message": "password changed successfully",'password':password})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

#############################My_Profile################################
@app.route('/fitzcube/my_profile_update',methods=['POST'])
def my_profile_update():
    try:
        data = mongo.db.register
        user_id = request.json['user_id']
        firstname = request.json['firstname']
        lastname = request.json['lastname']
        desgination = request.json['desgination']
        profession = request.json['profession']
        company_name = request.json['company_name']
        age = request.json['age']
        say_about_us = request.json['say_about_us']
        location = request.json['location']
        profile_pic = request.json['profile_pic']
        profile_pic = profile_pic.encode()
        profile_path = "/var/www/html/fitzcube/myprofile/" + str(firstname) + '.' + 'jpg'
        mongo_db_path = "/myprofile/" + str(firstname) + '.' + 'jpg'
        with open(profile_path, "wb") as fh:
            fh.write(base64.decodebytes(profile_pic))
        updated_time = strftime("%Y/%m/%d %H:%M:%S %I%p")
        data.find_one_and_update({'UserId':user_id},{'$set':{'FirstName': firstname, 'LastName': lastname,'Desgination':desgination,'Age': age,'ProfilePic':mongo_db_path,
                                'Location': location,'Profession':profession,'CompanyName':company_name,'Sayaboutus':say_about_us,'UpdatedTime': updated_time}})
        output = []
        details = data.find({'UserId':user_id})
        for j in details:
            output.append({'user_id': j['UserId'],'firstname': j['FirstName'],'lastname': j['LastName'], 'emailid': j['EmailId'],'password': j['Password'],
                           'age':j['Age'],'mobilenumber': j['MobileNumber'], 'gender': j['Gender'],'location':j['Location'],'desgination':j['Desgination'],
                           'profession':j['Profession'],'company_name':j['CompanyName'],'say_about_us':j['Sayaboutus'],'profile_pic':j['ProfilePic'],
                           'updated_time': j['UpdatedTime']})
        return jsonify({'status': 'success','message': 'Profile updated successfully','result': output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

@app.route('/fitzcube/profile_list', methods=['POST'])
def profile_list():
    try:
        data = mongo.db.register
        user_id = request.json['user_id']
        details = data.find({'UserId': user_id})
        output_list = []
        for j in details:
            temp_dict = {}
            temp_dict['user_id'] = j['UserId']
            temp_dict['firstname'] = j['FirstName']
            temp_dict['lastname'] = j['LastName']
            temp_dict['mobilenumber'] = j['MobileNumber']
            temp_dict['emailid'] = j['EmailId']
            temp_dict['password'] = j['Password']
            temp_dict['gender'] = j['Gender']

            if 'Location' not in j.keys():
                temp_dict['location'] = ""
            else:
                temp_dict['location'] = j['Location']

            if 'Age' not in j.keys():
                temp_dict['age'] = ''
            else:
                temp_dict['age'] = j['Age']

            if 'CompanyName' not in j.keys():
                temp_dict['company_name'] = ''
            else:
                temp_dict['company_name'] = j['CompanyName']

            if 'ProfilePic' not in j.keys():
                temp_dict['profile_pic'] = ''
            else:
                temp_dict['profile_pic'] = j['ProfilePic']

            if 'Desgination' not in j.keys():
                temp_dict['desgination'] = ''
            else:
                temp_dict['desgination'] = j['Desgination']

            if 'Profession' not in j.keys():
                temp_dict['profession'] = ''
            else:
                temp_dict['profession'] = j['Profession']

            if 'Sayaboutus' not in j.keys():
                temp_dict['say_about_us'] = ''
            else:
                temp_dict['say_about_us'] = j['Sayaboutus']

            if 'Account' not in j.keys():
                temp_dict['type_account'] = ''
            else:
                temp_dict['type_account'] = j['Account']

            output_list.append(temp_dict)

        return jsonify({"status": "success", "message": "List of Profile", "result": output_list})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

@app.route('/fitzcube/user_account',methods=['POST'])
def user_account():
    try:
        data = mongo.db.register
        user_id = request.json['user_id']
        type_account = request.json['type_account']
        details = data.find({'UserId': user_id})
        output = []
        if type_account == 'public':
            data.find_one_and_update({'UserId': user_id}, {'$set': {'Account': type_account}})
            for j in details:
                temp_dict = {}
                if 'UserId' not in j.keys():
                    temp_dict['user_id'] = ''
                else:
                    temp_dict['user_id'] = j['UserId']
                if 'FirstName' not in j.keys():
                    temp_dict['firstname'] = ''
                else:
                    temp_dict['firstname'] = j['FirstName']
                if 'LastName' not in j.keys():
                    temp_dict['lastname'] = ''
                else:
                    temp_dict['lastname'] = j['LastName']
                if 'MobileNumber' not in j.keys():
                    temp_dict['mobilenumber'] = ''
                else:
                    temp_dict['mobilenumber'] = j['MobileNumber']
                if 'EmailId' not in j.keys():
                    temp_dict['emailid'] = ''
                else:
                    temp_dict['emailid'] = j['EmailId']
                if 'Password' not in j.keys():
                    temp_dict['password'] = ''
                else:
                    temp_dict['password'] = j['Password']
                if 'Gender' not in j.keys():
                    temp_dict['gender'] = ''
                else:
                    temp_dict['gender'] = j['Gender']
                if 'Location' not in j.keys():
                    temp_dict['location'] = ""
                else:
                    temp_dict['location'] = j['Location']
                if 'Age' not in j.keys():
                    temp_dict['age'] = ''
                else:
                    temp_dict['age'] = j['Age']
                if 'CompanyName' not in j.keys():
                    temp_dict['company_name'] = ''
                else:
                    temp_dict['company_name'] = j['CompanyName']
                if 'ProfilePic' not in j.keys():
                    temp_dict['profile_pic'] = ''
                else:
                    temp_dict['profile_pic'] = j['ProfilePic']
                if 'Desgination' not in j.keys():
                    temp_dict['desgination'] = ''
                else:
                    temp_dict['desgination'] = j['Desgination']
                if 'Profession' not in j.keys():
                    temp_dict['profession'] = ''
                else:
                    temp_dict['profession'] = j['Profession']
                if 'Sayaboutus' not in j.keys():
                    temp_dict['say_about_us'] = ''
                else:
                    temp_dict['say_about_us'] = j['Sayaboutus']
                if 'Account' not in j.keys():
                    temp_dict['type_account'] = ''
                else:
                    temp_dict['type_account'] = j['Account']
                output.append(temp_dict)
            return jsonify({'status': 'success','message': 'user account updated successfully','result': output})
        elif type_account == 'private':
            data.find_one_and_update({'UserId': user_id}, {'$set': {'Account': type_account}})
            for q in details:
                temp_dict1 = {}
                if 'UserId' not in q.keys():
                    temp_dict1['user_id'] = ''
                else:
                    temp_dict1['user_id'] = q['UserId']
                if 'FirstName' not in q.keys():
                    temp_dict1['firstname'] = ''
                else:
                    temp_dict1['firstname'] = q['FirstName']
                if 'LastName' not in q.keys():
                    temp_dict1['lastname'] = ''
                else:
                    temp_dict1['lastname'] = q['LastName']
                if 'Desgination' not in q.keys():
                    temp_dict1['desgination'] = ''
                else:
                    temp_dict1['desgination'] = q['Desgination']
                if 'Profession' not in q.keys():
                    temp_dict1['profession'] = ''
                else:
                    temp_dict1['profession'] = q['Profession']
                if 'CompanyName' not in q.keys():
                    temp_dict1['company_name'] = ''
                else:
                    temp_dict1['company_name'] = q['CompanyName']
                output.append(temp_dict1)
            return jsonify({'status': 'success', 'message': 'user account updated successfully', 'result': output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

######################################ABOUTFitzcube#####################################################################
@app.route('/fitzcube/about_fitzcube', methods=['POST'])
def dukan():
    data = mongo.db.About_Fitzcube
    type = request.json['type']
    if type == "AboutUs":
        details = data.find_one({"Type": type})
        output = []
        output_dict = {'type': type,'path': details['Path']}
        output.append(output_dict)
        if details['Path'] != 0:
            return jsonify({"status": "success", "message": "AboutUs document", "result": output})
        else:
            return jsonify({"status": "failure", "message": "AboutUs data not get it."})
    elif type == "Terms&Conditions":
        details = data.find_one({"Type": type})
        output = []
        output_dict = {'type': type, 'path': details['Path']}
        output.append(output_dict)
        if details['Path'] != 0:
            return jsonify({"status": "success", "message": "Terms&Condition document", "result": output})
        else:
            return jsonify({"status": "failure", "message": "Did not get Terms&Condition document"})
    elif type == "PrivacyPolicy":
        details = data.find_one({"Type": type})
        output = []
        output_dict = {'type': type, 'path': details['Path']}
        output.append(output_dict)
        if details['Path'] != 0:
            return jsonify({"status": "success", "message": "privacy_policy document", "result": output})
        else:
            return jsonify({"status": "failure", "message": "Did not get privacy_policy document"})
    else:
        return jsonify({"status": "failure", "message": "Didn't get any data"})

######################################Events############################################
@app.route('/fitzcube/Create_event',methods=['POST'])
def Create_event():
    try:
        data = mongo.db.Event
        event_name = request.json['event_name']
        start_date = request.json['start_date']
        end_date = request.json['end_date']
        start_time = request.json['start_time']
        end_time = request.json['end_time']
        location = request.json['location']
        event_pic = request.json['event_pic']
        event_pic = event_pic.encode()
        event_path = "/var/www/html/fitzcube/event/" + str(event_name) + '.' + 'jpg'
        mongo_db_path = "/event/" + str(event_name) + '.' + 'jpg'
        with open(event_path, "wb") as fh:
            fh.write(base64.decodebytes(event_pic))
        updated_time = strftime("%Y/%m/%d %H:%M:%S %I%p")
        even_id_list = [i['EventId'] for i in data.find()]
        if len(even_id_list) is 0:
            event_id = 1
        else:
            event_id = int(even_id_list[-1]) + 1
        output = []
        data.insert({'EventId':event_id,'EventName':event_name,'StartDate':start_date,'EndDate':end_date,'StartTime':start_time,'EndTime':end_time,
                     'EventPic':mongo_db_path,'Location':location,'UpdatedTime':updated_time})
        output.append({'event_id':event_id,'event_name':event_name,'start_date':start_date,'end_date':end_date,'start_time':start_time,'end_time':end_time,
                       'event_pic':mongo_db_path,'location':location,'updated_time':updated_time})
        return jsonify({'status':"success",'message':'event create successfully','result':output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))


@app.route('/fitzcube/Add_Friend_Delete_Friend', methods=['POST'])
def Add_Friend_Delete_Friend():
    try:
        friends = mongo.db.Friendlist
        # print("friend db created")
        user_db = mongo.db.register
        user = request.json['user']
        print(user)##main user_id
        updated_time = strftime("%d/%m/%Y %H:%M:%S %I%p")
        friend = request.json['friend']
        print(friend)### friend_user_id
        f_info = user_db.find({'UserId': friend})
        print(f_info)
        for f in f_info:
            f_id= f[friend]
            print(f_id)
        return "ok"
    except:
        return "not ok"


    #     friend_info = friends.find({'Friend_user_id': friend})
    #     output = []
    #     for f in friend_info:
    #         friend_id = f['Friend_user_id']
    #         if friend_id == friend:
    #             return "user already exists in friends list"
    #     else:
    #         # info = user_db.find({'UserId': friend})
    #         for i in info:
    #             f_id = i['UserId']
    #             if f_id == friend:
    #                 friends.insert({'main_user':user, 'Friend_user_id':friend, "Friend_Name":f_id['FirstName']})
    #                 output.append({'main_user':user, 'Friend_user_id':friend, "Friend_Name":f_id['FirstName']})
    #                 return "friend added successfully"
    #         return jsonify({"message": "Add successful","result": output})
    #
    # except Exception as e:
    #     return jsonify(status="Fail", message=str(e))
    #


@app.route('/get_users', methods=['GET'])
def get_users():
    register = mongo.db.register
    data= register.find()
    output=[]
    for i in register.find():
        output.append({'user_id':i['UserId'],'name':i['FirstName']})
    return jsonify({'output':output})


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=9000, debug=True, threaded=True)
    app.run(debug=True)