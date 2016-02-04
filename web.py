#!/usr/bin/env python

import logging
import json
import extlibs.bottle as bottle

import finduser.data
import settings

APP = bottle.Bottle()
DAO = finduser.data.Access(settings.db_default_properties, settings.db_dirty_user_refresh)

@APP.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    bottle.response.headers['Access-Control-Allow-Origin'] = '*'
    bottle.response.headers['Access-Control-Allow-Methods'] = \
        'PUT, GET, POST, DELETE, OPTIONS'
    bottle.response.headers['Access-Control-Allow-Headers'] = \
        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@APP.route('/<filename:re:.*\.(css|js|jpg|png|gif|ico|ttf|eot|woff|woff2|svg|jsr|html)>')
def static_files(filename):
    return bottle.static_file(filename, root='static/')

@APP.route('/')
def hello():
    return bottle.static_file('index.html', root='static/')

@APP.route('/user/<cip>', method=['POST'])
def touch_user(cip):
    """Enforce the database the update the information for user <cip>."""
    DAO.touch_user({"cip": cip, "dirty": True, "lastUpdate": 0.0})

@APP.route('/finduser/model')
def user_model():
    """Model to build the user interfaces."""
    model = {
        "product": {}
    }
    for field_name, field_type in DAO.get_product_fields().items():
        model["product"][field_name] = str(field_type.__name__)
    return json.dumps(model)

@APP.route('/finduser', method=['POST'])
def get_users():
    request = bottle.request.body.read().decode(settings.default_encoding)
    logging.info("Find user: %s" % (request))
    try:
        json_obj = json.loads(request)
    except json.decoder.JSONDecodeError:
        return bottle.abort(400, \
            "I'm unable to parse the JSON string sent: %s" % (request))

    try:
        cip = DAO.get_user_by_properties(json_obj)
        return json.dumps(cip)
    except AssertionError:
        return bottle.abort(400, \
            "JSON being sent doesn't match the expected schema: %s" % (request))
    except LookupError:
        return bottle.abort(404, "Unable to find a user matching the criteriae: %s." % (request))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    bottle.run(APP, host=settings.web_address, port=settings.web_port, debug=True)
