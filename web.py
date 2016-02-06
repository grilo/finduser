#!/usr/bin/env python

import logging
import json
import extlibs.bottle as bottle

import settings
import finduser.data
import finduser.plugin

APP = bottle.Bottle()
DAO = finduser.data.Access(settings.db_default_properties, settings.db_dirty_user_refresh)
PLUGINS = finduser.plugin.Manager(settings.plugins_path)
for k, v in PLUGINS.get_plugins().items():
    DAO.generate_model(k, v.get_schema())


@APP.hook('after_request')
def enable_cors():
    """ You need to add some headers to each request.

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

@APP.route('/user/<personId>', method=['POST'])
def refresh_user(personId):
    """Enforce the database the update the information for user <personId>."""
    DAO.refresh_user(personId)

@APP.route('/finduser/model')
def user_model():
    """Model to build the user interface."""
    model = {}
    for name, plugin in PLUGINS.get_plugins().items():
        model[name] = {}
        for field_name, field_type in plugin.get_schema().items():
            if field_type == 'date':
                model[name][field_name] = 'date'
            else:
                model[name][field_name] = str(field_type.__name__)
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
        personId = DAO.get_user_by_properties(json_obj)
        return json.dumps(personId)
    except AssertionError:
        return bottle.abort(400, \
            "JSON being sent doesn't match the expected schema: %s" % (request))
    except LookupError:
        return bottle.abort(404, "Unable to find a user matching the criteriae: %s." % (request))


if __name__ == '__main__':
    logging.basicConfig(format=settings.log_format)
    logging.getLogger().setLevel(getattr(logging, settings.log_level.upper()))
    bottle.run(APP, host=settings.web_address, port=settings.web_port, debug=True)
