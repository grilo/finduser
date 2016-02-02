#!/usr/bin/env python

import logging
import json
import extlibs.bottle as bottle

import data
import settings

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

@app.route('/<filename:re:.*\.(css|js|jpg|png|gif|ico|ttf|eot|woff|woff2|svg|jsr|html)>')
def static_files(filename):
    return bottle.static_file(filename, root='static/')

@app.route('/')
def hello():
    return bottle.static_file('index.html', root='static/')

"""
    Enforce the database the update the information for user <cip>
"""
@app.route('/user/<cip>', method=['POST'])
def touch_user(cip):
    dao.touch_user({"cip": cip, "dirty": True, "lastUpdate": 0.0})

"""
    Model to build the user interfaces
"""
@app.route('/finduser/model')
def user_model():
    model = {
        "product": {}
    }
    for field_name, field_type in dao.get_product_fields().items():
        model["product"][field_name] = str(field_type.__name__)
    return json.dumps(model)

@app.route('/finduser', method=['POST'])
def get_users():
    request = bottle.request.body.read().decode(settings.default_encoding)
    logging.info("Find user: %s" % (request))
    json_obj = json.loads(request)

    param_count = 0
    if k, v in json_obj.items():
        param_count += len(v)
    if param_count == 0:
        return bottle.abort(400, "No query parameters sent, refusing to return a value.")

    cip = dao.get_user_by_properties(json_obj)
    if cip == "":
        return bottle.abort(404, "Unable to find a user matching the criteriae.")

    return json.dumps(cip)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    bottle.run(app, host=settings.web_address, port=settings.web_port, debug=True)
