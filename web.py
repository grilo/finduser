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

@app.route('/finduser', method=['POST'])
def get_users():
    request = bottle.request.body.read().decode('utf8')
    cip = dao.get_user_by_properties(json.loads(request))
    if cip == "":
        bottle.abort(400, "Unable to find a user matching the criteriae.")
    return json.dumps(cip)

@app.route('/user/<cip>', method=['POST'])
def touch_user(cip):
    dao.touch_user({"cip": cip, "dirty": True, "lastUpdate": 0.0})

@app.route('/<filename:re:.*\.(css|js|jpg|png|gif|ico|ttf|eot|woff|woff2|svg|jsr|html)>')
def static_files(filename):
    return bottle.static_file(filename, root='')

@app.route('/')
def hello():
    f = open('static/index.html')
    contents = f.read()
    f.close()
    return contents

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    bottle.run(app, host='localhost', port=8080, debug=True)
