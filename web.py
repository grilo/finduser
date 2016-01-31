#!/usr/bin/env python

import logging
import json
import bottle

import data

app = bottle.Bottle()
dao = data.Access()

@app.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    bottle.response.headers['Access-Control-Allow-Origin'] = '*'
    bottle.response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@app.route('/user', method=['GET'])
def get_users():
    properties = {}
    for k, v in bottle.request.query.decode().items():
        properties[k] = v
    return json.dumps(dao.get_user_by_properties(properties))

@app.route('/user/<cip>', method=['POST'])
def touch_user(cip):
    dao.touch_user({"cip": cip})

@app.route('/')
def hello():
    f = open('index.html')
    contents = f.read()
    f.close()
    return contents

if __name__ == '__main__':
    bottle.run(app, host='localhost', port=8080, debug=True)
