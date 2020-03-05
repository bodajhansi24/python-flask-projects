import csv
from os.path import join
from bson.objectid import ObjectId
import flask_login
from flask_pymongo import PyMongo
from flask import stream_with_context, Response, make_response
from bson.objectid import ObjectId
import datetime
# import datetime
from flask_cors import CORS, cross_origin
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, current_user, get_jwt_identity, jwt_required,jwt_required, create_access_token
from itsdangerous import URLSafeTimedSerializer
import os
from flask import Flask, render_template, request, jsonify, json, session, redirect, url_for, send_from_directory
from flask.json import jsonify
from pymongo import MongoClient
import base64
from flask_login import login_user, logout_user, login_required, LoginManager
import string
from werkzeug.utils import secure_filename
from datetime import date

app=Flask(__name__)
CORS(app, supports_credentials= True)

# client = MongoClient('localhost:27017')
client = MongoClient('3.105.128.235:6909')

app.config['MONGO_DBNAME']='fitzcube'
app.config['MONGO_URI']='mongodb://3.105.128.235:6909/fitzcube'
app.config['JWT_SECRET_KEY']='fugenx'

mongo=PyMongo(app)
b_crypt=Bcrypt(app)
jwt=JWTManager(app)

s = URLSafeTimedSerializer('1234')


CORS(app)
APP_ROOT= os.path.dirname(os.path.abspath(__file__))
UPLOAD= '/static/Videos'
if not os.path.exists(UPLOAD):
    os.makedirs(UPLOAD)

ALLOWED_EXTENSIONS = ['mp4','']
UPLOAD_FOLDER= os.path.join(APP_ROOT,UPLOAD)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JWT_SECRET_KEY']='fugenx'

# mongo=PyMongo(app)
b_crypt=Bcrypt(app)
jwt=JWTManager(app)

s = URLSafeTimedSerializer('1234')
"""

@app.route('/upload_video', methods= ['POST','GET'])
@cross_origin(supports_credentials=True)
def upload_video():
    db = client.fitzcube
    filenames=[]
    output=[]
    try:
        if "Videos" in db.list_collection_names():
            if request.method == 'POST' and 'file' in request.files:
                for f in request.files.getlist('file'):
                    os.makedirs(os.path.join(UPLOAD_FOLDER), exist_ok=True)
                    filename = secure_filename(f.filename)
                    filenames.append(filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    output.append(f.filename)
                    f.save(filepath)
                    file_id_count = len(list(db.Videos.find()))
                    file_id = "File" + str(file_id_count)
                    upload_date=datetime.date.today().strftime('%Y/%m/%d')
                    db.Videos.insert({'filename':filename,'file_path': filepath, 'file_id': file_id, 'upload_date':upload_date})
                return jsonify({"status": "success", "message": "insert successful"})
        else:
            db.create_collection('Videos', capped=True, size=5e+8, max=5)
            for f in request.files.getlist('file'):
                os.makedirs(os.path.join(UPLOAD_FOLDER), exist_ok=True)
                filename = secure_filename(f.filename)
                filenames.append(filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                output.append(f.filename)
                f.save(filepath)
                file_id_count = len(list(db.Videos.find()))
                file_id = "File" + str(file_id_count)
                upload_date = datetime.date.today().strftime('%Y/%m/%d')
                db.Videos.insert({'filename':filename,'file_path': filepath, 'file_id': file_id, 'upload_date':upload_date})
            return jsonify({"status": "success", "message": "insert successful"})
    except Exception as e:
        return str(e)



@app.route('/show_videos', methods=['POST', 'GET'])
def show_videos():
    db= client.fitzcube
    coll= db.Videos
    data= coll.find()
    output=[]
    for d in data:
        filename= d['filename']
        output.append(filename)
    for i in output:
        return send_from_directory(UPLOAD_FOLDER, i)

    # return jsonify({'result':output})



@app.route('/show_file/<file_id>', methods=['POST','GET'])
def show_file(file_id):
    db= client.fitzcube
    coll= db.Videos
    data= coll.find({'file_id':file_id})
    for f in data:
        id= f['file_id']
        if id== file_id:
            filename= f['filename']
            return send_from_directory(UPLOAD_FOLDER, filename)
    else:
        return "No Data Found"




@app.route('/stream_video/<file_id>', methods=['POST','GET'])
def stream_video(file_id):
    db= client.fitzcube
    coll= db.Videos
    file= coll.find({'file_id':file_id})
    for f in file:
        id= f['file_id']
        filepath= f['file_path']
        file= f['filename']
        if id is None:
            return "No Data"
        if id is not None:
            file_size= os.path.getsize(filepath)
            fh= open(filepath, 'rb')
            return Response(fh,
                            mimetype='application/octet-stream',
                            headers=[
                                ('Content-Length', str(file_size)),
                                ('Content-Disposition', "attachment; filename=\"%s\"" % file),
                            ],
                            direct_passthrough=True)
            #
            #
            # raw_bytes=""
            # with open (filepath, 'rb') as r:
            #     for line in r:
            #         raw_bytes = raw_bytes + line
            #     response = make_response(raw_bytes)
            #     response.headers['Content-Type'] = "application/octet-stream"
            #     response.headers['Content-Disposition'] = "inline; filename=" + file
            #     return response
    else:
        return "Couldnt play file"



@app.route('/show_files', methods=['POST','GET'])
def show_files():
    db= client.fitzcube
    coll= db.Videos
    output=[]
    result=[]
    data= coll.find()
    files=[]
    for f in data:
        filename= f['filename']
        filepath= f['file_path']
        files.append({'filename':filename, 'filepath':filepath})
    return jsonify({'result':files})
"""


@app.route('/last_week_videos', methods=['POST','GET'])
def last_week_videos():
    try:
        db = client.fitzcube
        videos = []
        coll = db.category

        data= coll.find()
        for d in data:
            posted_date=datetime.datetime.strptime(d['UpdatedTime'],'%Y/%m/%d %H:%M:%S %I%p')
            print(posted_date)
            current_date=date.today()
            time_delta= current_date -posted_date.date()
            print(time_delta)
            print(time_delta.days)
            if time_delta.days<8:
                file= d['Video']
                videos.append({'file_path':file,'comments':d['comments'],'likes':d['likes']})
            return jsonify({'result':videos})
        else:
            return "No Data Found"
    except Exception as e:

        return jsonify(status="Fail", message=str(e))


@app.route('/all_videos', methods=['GET'])
def get_all_videos():
    try:
        db = client.fitzcube
        videos = []
        coll = db.category
        data = coll.find()
        for d in data:
            posted_date = datetime.datetime.strptime(d['UpdatedTime'], '%Y/%m/%d %H:%M:%S %I%p')
            file = d['Video']
            videos.append({'file_path': file, 'date': posted_date,'comments':d['comments'],'likes':d['likes']})
        return jsonify({'result': videos})
    except Exception as e:

        return jsonify(status="Fail", message=str(e))


@app.route('/last_month_videos', methods=['GET'])
def last_month_videos():
    try:
        db = client.fitzcube
        # count=0
        # likes = 0
        videos = []
        output = []
        coll = db.category
        friends_db = db.friends


        data = coll.find()
        for d in data:
            posted_date = datetime.datetime.strptime(d['UpdatedTime'], '%Y/%m/%d %H:%M:%S %I%p')
            posted_month= posted_date.month
            # print(posted_month)
            current_date= date.today()
            current_month= current_date.month
            # print(current_month)
            # print(type(current_month))
            if current_month-1 == posted_month:
                file= d['Video']
                videos.append(file)
        return jsonify({'result':videos})
    except Exception as e:

        return jsonify(status="Fail", message=str(e))
    # else:
    #     return "No Videos posted in last month"


@app.route('/recent_videos', methods=['POST', 'GET'])
def recent_videos():
    try:
        db = client.fitzcube
        videos = []
        coll = db.category
        coll2 = db.user_activities
        type = request.json['type']
        Id = request.json['Id']
        if type == 'comments':
            comments = request.json['comments']

            #coll2.insert({"Video": Video})
            coll.update({"Id": Id}, {"$push": {'comments': comments}})
        elif type == 'likes':
            likes = request.json['likes']
            if likes == True:
                likes += 0
                coll.update({"Id": Id}, {"$inc": {'likes': likes}})
                coll2.update({"Id": Id}, {"$inc": {'likes': likes}})
            elif likes==False:
                likes -= 1
                coll.update({"Id": Id}, {"$inc": {'likes': likes}})
                coll2.update({"Id": Id}, {"$inc": {'likes': likes}})


        for d in coll.find().sort('Id', -1).limit(5):
            videos.append({'file_path': d['Video']})

        return jsonify({'result': videos})

    except Exception as e:

        return jsonify(status="Fail", message=str(e))


@app.route('/share_videos/<UserId>', methods=['POST', 'GET'])
def share_videos(UserId):
    try:
        db = client.fitzcube
        coll = db.category
        friends_db = db.friends
        share_db = db.share
        FriendId = request.json['FriendId']
        Video = request.json['Video']
        # share_db.insert({"Video": Video,'UserId':UserId,'FriendId':FriendId})
        # return redirect(url_for('send_file',filename=Video))



        user_info = friends_db.find({'FriendId': FriendId})
        for user in user_info:
            if user == FriendId:
                    return 'ok'
        return redirect(url_for('send_file', filename=Video))


    except Exception as e:

        return jsonify(status="Fail", message=str(e))



@app.route('/uploads/<filename>')
@cross_origin(supports_credentials=True)
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)



if __name__== '__main__':
    app.run(debug= True)



