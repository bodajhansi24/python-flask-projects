from flask import Flask,request,jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from time import strftime
import re,os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "/var/www/html/fitzcube"
ALLOWED_EXTENSIONS = set(['mp4', 'mov','wmv', 'flv', 'avi'])
FILE_ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc','docx'])

app = Flask(__name__)
app.config["MONGO_DBNAME"] = "fitzcube"
# app.config["MONGO_URI"] = "mongodb://localhost:27017/fitzcube"
app.config["MONGO_URI"] = "mongodb://3.105.128.235:6909/fitzcube"
mongo = PyMongo(app)
CORS(app)

##########################################################Admin Login###################################################
@app.route('/fitzcube/admin_login', methods=['POST'])
def admin_login():
    data = mongo.db.Admin_Login
    username = str(request.json['username'])
    password = str(request.json['password'])
    if re.match('\S+@\S+', str(username)) != None:
        flag = 'emailid'
    elif re.match('\d{10}', username) != None:
        flag = 'mobilenumber'
    if flag == 'emailid':
        q = data.find_one({'EmailId': username})
        if q == None:
            return jsonify({'status': 'failure', 'message': "emailId not found"})
        elif q != None and q['Password'] != password:
            return jsonify({'status': 'failure', 'message': 'Password is wrong'})
        elif q != None and q['Password'] == password:
            temp_dict={}
            temp_dict['userid']=q['UserId']
            temp_dict['firstname']=q['FirstName']
            temp_dict['lastname']=q['LastName']
            temp_dict['mobilenumber']=q['MobileNumber']
            temp_dict['emailid']=q['EmailId']
            temp_dict['password'] = q['Password']
            temp_dict['updated_time']=q['UpdatedTime']
            return jsonify({'status': "success", 'message': "login successful","result":[temp_dict]})
    elif flag == 'mobilenumber':
        q = mongo.db.Admin_Login.find_one({'MobileNumber': username})
        if q == None:
            return jsonify({'status': 'failure', 'message': "MobileNumber not found"})
        elif q != None and q['Password'] != password:
            return jsonify({'status': 'failure', 'message': 'Password is wrong'})
        elif q != None and q['Password'] == password:
            temp_dict={}
            temp_dict['userid'] = q['UserId']
            temp_dict['firstname']=q['FirstName']
            temp_dict['lastname']=q['LastName']
            temp_dict['mobilenumber']=q['MobileNumber']
            temp_dict['emailid']=q['EmailId']
            temp_dict['password'] = q['Password']
            temp_dict['updated_time'] = q['UpdatedTime']
            return jsonify({'status': 'success', 'message': "login successful","result":[temp_dict]})

###############################################################User_Management##########################################
@app.route('/fitzcube/user_details', methods=['GET'])
def profile_list():
    data = mongo.db.register
    output_list = []
    for j in data.find():
        temp_dict = {}
        temp_dict['user_id'] = j['UserId']
        temp_dict['firstname'] = j['FirstName']
        temp_dict['lastname'] = j['LastName']
        temp_dict['mobilenumber'] = j['MobileNumber']
        temp_dict['emailid'] = j['EmailId']
        temp_dict['password'] = j['Password']
        if 'Gender' not in j.keys():
            temp_dict['gender'] = ""
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
        if 'Company Name' not in j.keys():
            temp_dict['company_name'] = ''
        else:
            temp_dict['company_name'] = j['CompanyName']
        if 'Profile Pic' not in j.keys():
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
        if 'Say about us' not in j.keys():
            temp_dict['say_about_us'] = ''
        else:
            temp_dict['say_about_us'] = j['Sayaboutus']
        if 'Account' not in j.keys():
            temp_dict['type_account'] = ''
        else:
            temp_dict['type_account'] = j['Account']
        output_list.append(temp_dict)
    return jsonify({"status": "success", "message": "List of Profile", "result": output_list})

#####################################################################uploadvideo#######################################
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload_video_image/<video_image>',methods=['POST'])
def upload_video(video_image):
    output = []
    if request.method == 'POST' and 'file' in request.files:
        for f in request.files.getlist('file'):
            os.makedirs(os.path.join(UPLOAD_FOLDER,str(video_image)), exist_ok=True)
            f.save(os.path.join(UPLOAD_FOLDER,str(video_image), secure_filename(f.filename)))
            video_image_path = os.path.join(UPLOAD_FOLDER,str(video_image),secure_filename(f.filename))
            output.append(str(video_image_path.split("/")[-2]) + '/' + str(video_image_path.split("/")[-1]))
        return jsonify({"status": "success", "output": output, "message": 'video saved successfully'})
    else:
        return jsonify({"status": "failure", "message": 'Error Occured, Please Try again'})

#########################################AboutUs&TermsandCondition&PtivacyPolicy#######################################
def alloweded_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in FILE_ALLOWED_EXTENSIONS

@app.route('/fitzcube/upload_file/<id>/<file>', methods=['GET','POST'])
def upload_file(id,file):
    data = mongo.db.About_Fitzcube
    output = []
    if request.method == 'POST' and 'file' in request.files:
        for f in request.files.getlist('file'):
            os.makedirs(os.path.join(UPLOAD_FOLDER,str(file)),exist_ok=True)
            f.save(os.path.join(UPLOAD_FOLDER,str(file),secure_filename(f.filename)))
            file_path = os.path.join(UPLOAD_FOLDER,str(file),secure_filename(f.filename))
            # data.insert({"Id":int(id),"Type": file,"Path":str(file_path.split("/")[-3]) + '/'+ str(file_path.split("/")[-2]) + '/' + str(file_path.split("/")[-1])})
            data.find_one_and_update({"Id": int(id)},{'$set':{"Type": file,"Path": str(file_path.split("/")[-3]) + '/' + str(file_path.split("/")[-2]) + '/' + str(file_path.split("/")[-1])}})
            output.append(str(file_path.split("/")[-3]) + '/'+ str(file_path.split("/")[-2]) + '/' + str(file_path.split("/")[-1]))
        return jsonify({"status": "success","output": output, "message": 'file saved successfully'})
    else:
        return jsonify({"status": "failure", "message": 'Error Occured, Please Try again'})

@app.route('/fitzcube/uplaod_files',methods=['GET'])
def uplaod_files():
    data = mongo.db.About_Fitzcube
    output = []
    for q in data.find():
        output.append({'id':q['Id'],'type':q['Type'],'file_path':q['Path']})
    return jsonify({'status': 'success', 'message': 'About Dukan data get successfully','result': output})

#########################################################YogaAndGym######################################################
@app.route('/fitzcube/add_category',methods=['POST'])
def add_category():
    try:
        data = mongo.db.category
        id  = int(request.json['id'])
        image = str(request.json['image'])
        title = str(request.json['title'])
        video = str(request.json['video'])
        sub_title = str(request.json['sub_title'])
        description = str(request.json['description'])
        updated_time = strftime("%Y/%m/%d %H:%M:%S %I%p")
        data.insert({'Id': id,'Image':image,'Title': title,'Video':video,'SubTitle':sub_title,'Description':description,'UpdatedTime':updated_time})
        output = [{'id':id,'image':image,'title':title,'video':video,'sub_title':sub_title,'description':description,'updated_time':updated_time}]
        return jsonify({'status': 'success', "message": "gym or yoga data successfully", "result": output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

@app.route('/fitzcube/get_category',methods=['GET'])
def get_category():
    try:
        data = mongo.db.category
        output = []
        for q in data.find():
            output.append({'id':q['Id'],'title':q['Title'],'video':q['Video'],'sub_title':q['SubTitle'],'description':q['Description'],'updated_time':q['UpdatedTime']})
        return jsonify({'status': 'success', 'message': 'all yoga or gym details get successfully', "result": output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

@app.route('/fitzcube/update_category',methods=['POST'])
def update_category():
    try:
        data = mongo.db.category
        id = int(request.json['id'])
        image = str(request.json['image'])
        title = str(request.json['title'])
        video = str(request.json['video'])
        sub_title = str(request.json['sub_title'])
        description = str(request.json['description'])
        updated_time = strftime("%Y/%m/%d %H:%M:%S %I%p")
        output = []
        data.find_one_and_update({'Id': id},{'$set':{'Image':image,'Title': title,'Video':video,'SubTitle':sub_title,'Description':description,'UpdatedTime':updated_time}})
        output.append({'id':id,'image':image,'title':title,'video':video,'sub_title':sub_title,'description':description,'updated_time':updated_time})
        return jsonify({'status': 'success', 'message': 'all yoga or gym details updated successfully', "result": output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

@app.route('/fitzcube/delete_category',methods=['POST'])
def delete_category():
    try:
        data = mongo.db.category
        id = int(request.json['id'])
        image = str(request.json['image'])
        video = str(request.json['video'])
        data.find_one_and_delete({'Id': id,'Image':image,'Video':video})
        return jsonify({'status': 'success', 'message': 'particular yoga or gym details deleted successfully'})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

#######################################################Recipe#############################################################
@app.route('/fitzcube/add_recipe',methods=['POST'])
def add_recipe():
    try:
        data = mongo.db.Recipe
        recipe_name = str(request.json['recipe_name'])
        ingredients = str(request.json['ingredients'])
        servings = str(request.json['servings'])
        mins_to_prepare = str(request.json['mins_to_prepare'])
        mins_of_cooking = str(request.json['mins_of_cooking'])
        recipe_image = str(request.json['recipe_image'])
        recipe_video = str(request.json['recipe_video'])
        nutrition_info = str(request.json['nutrition_info'])
        cooking_steps = str(request.json['cooking_steps'])
        quick_info = str(request.json['quick_info'])
        updated_time = strftime("%Y/%m/%d %H:%M:%S %I%p")

        recipe_id_list = [i['RecipeId'] for i in data.find()]
        if len(recipe_id_list) is 0:
            recipe_id = 1
        else:
            recipe_id = int(recipe_id_list[-1]) + 1

        data.insert({'RecipeId':recipe_id,'RecipeName':recipe_name,'Ingredients':ingredients,'Servings':servings,'MinstoPrepare':mins_to_prepare,
                     'MinsofCooking':mins_of_cooking,'RecipeImage':recipe_image,'RecipeVideo':recipe_video,'NutritionInfo':nutrition_info,
                     'CookingSteps':cooking_steps,'QuickInfo':quick_info,'UpdatedTime':updated_time})
        output = []
        output.append({'recipe_id':recipe_id,'recipe_name':recipe_name,'ingredients':ingredients,'servings':servings,'mins_to_prepare':mins_to_prepare,
                       'mins_of_cooking':mins_of_cooking,'recipe_image':recipe_image,'recipe_video':recipe_video,'nutrition_info':nutrition_info,
                       'cooking_steps':cooking_steps,'quick_info':quick_info,'updated_time':updated_time})
        return jsonify({'status':'success','message':'Recipe Details added successfully','result':output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

@app.route('/fitzcube/get_recipe',methods=['GET'])
def get_recipe():
    try:
        data = mongo.db.Recipe
        output= []
        for q in data.find():
            output.append({'recipe_id':q['RecipeId'],'recipe_name':q['RecipeName'],'ingredients':q['Ingredients'],'servings':q['Servings'],
                           'mins_to_prepare':q['MinstoPrepare'],'mins_of_cooking':q['MinsofCooking'],'recipe_image':q['RecipeImage'],
                           'recipe_video':q['RecipeVideo'],'nutrition_info':q['NutritionInfo'],'cooking_steps':q['CookingSteps'],
                           'quick_info':q['QuickInfo'],'updated_time':q['UpdatedTime']})
        return jsonify({'status': 'success', 'message': 'all recipe details get successfully', "result": output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

@app.route('/fitzcube/edit_recipe',methods=['POST'])
def edit_recipe():
    try:
        data = mongo.db.Recipe
        recipe_id = int(request.json['recipe_id'])
        recipe_name = str(request.json['recipe_name'])
        ingredients = str(request.json['ingredients'])
        servings = str(request.json['servings'])
        mins_to_prepare = str(request.json['mins_to_prepare'])
        mins_of_cooking = str(request.json['mins_of_cooking'])
        recipe_image = str(request.json['recipe_image'])
        recipe_video = str(request.json['recipe_video'])
        nutrition_info = str(request.json['nutrition_info'])
        cooking_steps = str(request.json['cooking_steps'])
        quick_info = str(request.json['quick_info'])
        updated_time = strftime("%Y/%m/%d %H:%M:%S %I%p")

        data.find_one_and_update({'RecipeId':recipe_id},{'$set':{'RecipeName':recipe_name,'Ingredients':ingredients,'Servings':servings,'MinstoPrepare':mins_to_prepare,
                     'MinsofCooking':mins_of_cooking,'RecipeImage':recipe_image,'RecipeVideo':recipe_video,'NutritionInfo':nutrition_info,
                     'CookingSteps':cooking_steps,'QuickInfo':quick_info,'UpdatedTime':updated_time}})
        output = []
        output.append({'recipe_id': recipe_id, 'recipe_name': recipe_name, 'ingredients': ingredients, 'servings': servings,'mins_to_prepare': mins_to_prepare,
                       'mins_of_cooking': mins_of_cooking, 'recipe_image': recipe_image, 'recipe_video': recipe_video,'nutrition_info': nutrition_info,
                        'cooking_steps': cooking_steps, 'quick_info': quick_info, 'updated_time': updated_time})
        return jsonify({'status': 'success', 'message': 'recipe details updated successfully', "result": output})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

@app.route('/fitzcube/delete_recipe',methods=['POST'])
def delete_recipe():
    try:
        data = mongo.db.Recipe
        recipe_id = int(request.json['recipe_id'])
        data.find_one_and_delete({'RecipeId':recipe_id})
        return jsonify({'status': 'success', 'message': 'particular recipe details deleted successfully'})
    except Exception as e:
        return jsonify(status="Fail", message=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9001, debug=True, threaded=True)

# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)