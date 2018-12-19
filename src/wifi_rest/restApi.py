# -*- coding: utf-8 -*-
#
# Jame Yu
#

## usage example:
#
# This api interface runs as stand-alone process.
# 
# api call from peer should access the urls as listed below:
# http://<hostname>:5003/captcha/<version>
# http://<hostname>:5003/captchaimg/<sessionid>
# http://<hostname>:5003/reg/<sessionid>/<imgid> #with registration form passed as parameters

import os
import sys
import logging
import uuid
import redis
import json
import hashlib
import base64

from captcha.image import ImageCaptcha

from flask import Flask, request, send_file, abort
from flask_restful import Resource, Api
from flask.json import jsonify
from flask_cors import CORS

from helper import ConnStrDBSession
from db_models import *

from conf import username, password

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d: %(levelname)s:%(funcName)s() - %(message)s')

dbConnStr = "mysql+pymysql://"+username+":"+password+"@127.0.0.1:3306/emqtt?charset=utf8" 

app = Flask(__name__)
CORS(app)
api = Api(app)

the_redis = redis.StrictRedis.from_url("redis://127.0.0.1:6379/2", socket_timeout=10)


def getTransactionInfo(sid):
    d = dict()
    try:
        d = json.loads(the_redis.get(sid))
    except:
        return None

    # found
    return d


def deleteTransaction(sid):
    try:
        the_redis.delete(sid)
    except:
        pass


def getDbEntry(sessionid):
    d = getTransactionInfo(sessionid)
    if d:
        if d.has_key('img_id'):
            return d['img_id']
    #if not found
    return None


def saveTransaction(sid, val):
    the_redis.set(name=sid,
                      value=val,
                      ex=300)


class wifiGenCaptcha(Resource):
    def get(self, version):

        # if it is version 1.0 then return v1.0 captcha
        if version == 'v1.0':
            uid = uuid.uuid4().hex.upper()
            assoc_id = uid[:12]
            img_id   = uid[-6:]
            saveTransaction(assoc_id, json.dumps({'img_id':img_id}))
 
            # then send back the association id to the client
            # the client could then use the association id to fetch the 
            # image generated from the image id (code) 
            return jsonify({'assoc_id':assoc_id})

        abort(404)
        
class wifiGenImg(Resource):
    def get(self, sessionid):

        # if we could find the imgid via the
        # association id, then return the image
        # otherwise fail it.
        if sessionid:
            imgid = getDbEntry(sessionid)
            if imgid:
                imgdata = self.genCaptcha(imgid)
                return send_file(imgdata, mimetype='image/png')

        abort(404)


    def genCaptcha(self, imgid):
        image = ImageCaptcha()
        return image.generate(imgid)


class wifiReg(Resource):
    def post(self, sessionid, imgid):
        if sessionid:
            img_id = getDbEntry(sessionid)
            #check the imgid
            if img_id == imgid:
                data = json.loads(request.form['data'])
                username = data['username']
                password = data['password']

                hashed_pass = hashlib.sha1(password.encode("utf8")).hexdigest()

                user_data = User(username=username,
                                 password=hashed_pass)

                acl_data = Acl(username=username,
                               allow=1,
                               access=3, 
                               topic="/"+username+"/#")

                #:save user info into mysqldb
                with ConnStrDBSession(dbConnStr) as session:
                    session.add(user_data)
                    session.add(acl_data)
                    session.commit()

                return jsonify({'result':'ok'})

        return jsonify({'result':'failed'})


class wifiAddUserDev(Resource):
    def post(self):
        data = json.loads(request.form['data'])
        username = data['username']
        password = data['password']
        hwid     = data['hwId']
        devtype  = data['devType']
        devname  = data['devName']
        data     = data['data']

        hashed_pass = hashlib.sha1(password.encode("utf8")).hexdigest()

        #:get user info from mysqldb
        with ConnStrDBSession(dbConnStr) as session:
            user = session.query(User).filter(User.username == username).filter(User.password == hashed_pass).first()
            if user:
                user_dev = session.query(Userdev).filter(Userdev.userid == user.id).filter(Userdev.hwid == hwid).first()
                if user_dev:
                    if user_dev.devname == devname:
                        #data already exist, just done.
                        return jsonify({'result':'ok'})
                    else:
                        #need to update the devname
                        user_dev.devname = devname
                        session.commit()
                        return jsonify({'result':'ok'})

                user_dev = Userdev(userid = user.id,
                                   hwid = hwid,
                                   devtype = int(devtype),
                                   devname = devname,
                                   data = data)

                session.add(user_dev)
                session.commit()

                return jsonify({'result':'ok'})

        return jsonify({'result':'failed'})

class wifiDelUserDev(Resource):
    def post(self):
        data = json.loads(request.form['data'])
        username = data['username']
        password = data['password']
        hwid     = data['hwId']

        hashed_pass = hashlib.sha1(password.encode("utf8")).hexdigest()

        #:get user info from mysqldb
        with ConnStrDBSession(dbConnStr) as session:
            user = session.query(User).filter(User.username == username).filter(User.password == hashed_pass).first()
            if user:
                user_dev = session.query(Userdev).filter(Userdev.userid == user.id).filter(Userdev.hwid == hwid).delete()
                session.commit()

            return jsonify({'result':'ok'})

        return jsonify({'result':'failed'})


class wifiLogin(Resource):
    def post(self):
        data = json.loads(request.form['data'])
        username = data['username']
        password = data['password']

        hashed_pass = hashlib.sha1(password.encode("utf8")).hexdigest()

        #:get user info from mysqldb
        with ConnStrDBSession(dbConnStr) as session:
            user = session.query(User).filter(User.username == username).filter(User.password == hashed_pass).first()
            if user:
                return jsonify({'result':'ok'})

        return jsonify({'result':'failed'})


class wifiListUserDev(Resource):
    def post(self):
        data = json.loads(request.form['data'])
        username = data['username']
        password = data['password']

        hashed_pass = hashlib.sha1(password.encode("utf8")).hexdigest()

        #:get user info from mysqldb
        with ConnStrDBSession(dbConnStr) as session:
            user = session.query(User).filter(User.username == username).filter(User.password == hashed_pass).first()
            if user:
                devlist = []
                user_dev_list = session.query(Userdev).filter(Userdev.userid == user.id).all()
                if user_dev_list:
                    for dev in user_dev_list:
                        devlist.append({'hwid': dev.hwid, 'devtype': dev.devtype, 'devname': dev.devname, 'data': dev.data})

                return jsonify({'result':'ok', 'data': devlist})

        return jsonify({'result':'failed'})

api.add_resource(wifiGenCaptcha, '/captcha/<version>')
api.add_resource(wifiGenImg, '/captchaimg/<sessionid>')
api.add_resource(wifiReg, '/reg/<sessionid>/<imgid>')
api.add_resource(wifiAddUserDev, '/adddev')
api.add_resource(wifiDelUserDev, '/deldev')
api.add_resource(wifiListUserDev, '/listdev')
api.add_resource(wifiLogin, '/login')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
