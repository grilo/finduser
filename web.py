#!/usr/bin/env python

import logging
import json
import bottle

import models

app = bottle.Bottle()

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
    parameters = {}
    for k, v in bottle.request.query.decode().items():
        parameters[k] = v
    return json.dumps(models.getquery(parameters))

@app.route('/')
def hello():
    f = open('index.html')
    contents = f.read()
    f.close()
    return contents

if __name__ == '__main__':
    bottle.run(app, host='localhost', port=8080, debug=True)
