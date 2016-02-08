#!/usr/bin/env python

import logging
import json
import extlibs.bottle as bottle

import settings
import finduser.data
import finduser.plugin


def main(dao, plugin_manager):
    app = bottle.Bottle()
    logging.basicConfig(format=settings.log_format)
    logging.getLogger().setLevel(getattr(logging, settings.log_level.upper()))

    @app.hook('after_request')
    def enable_cors():
        """ You need to add some headers to each request.

        Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
        """
        bottle.response.headers['Access-Control-Allow-Origin'] = '*'
        bottle.response.headers['Access-Control-Allow-Methods'] = \
            'PUT, GET, POST, DELETE, OPTIONS'
        bottle.response.headers['Access-Control-Allow-Headers'] = \
            'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

    @app.route('/<filename:re:.*\.(css|js|jpg|png|gif|ico|ttf|eot|woff|woff2|svg|jsr|html)>')
    def static_files(filename):
        return bottle.static_file(filename, root='static/')

    @app.route('/')
    def hello():
        return bottle.static_file('index.html', root='static/')

    @app.route('/user/<personId>', method=['POST'])
    def refresh_user(personId):
        """Enforce the database the update the information for user <personId>."""
        dao.refresh_user(personId)

    @app.route('/finduser/model')
    def user_model():
        """Model to build the user interface."""
        model = {}
        for name, plugin in plugin_manager.get_plugins().items():
            model[name] = {}
            for field_name, field_type in plugin.get_schema().items():
                model[name][field_name] = field_type
        return json.dumps(model)

    @app.route('/finduser', method=['POST'])
    def get_users():
        request = bottle.request.body.read().decode(settings.default_encoding)
        logging.info("Find user: %s" % (request))
        try:
            json_obj = json.loads(request)
        except json.decoder.JSONDecodeError:
            return bottle.abort(400, \
                "I'm unable to parse the JSON string sent: %s" % (request))

        try:
            personId = dao.get_user_by_properties(json_obj)
            return json.dumps(personId)
        except AssertionError:
            return bottle.abort(400, \
                "JSON being sent doesn't match the expected schema: %s" % (request))
        except LookupError:
            return bottle.abort(404, "Unable to find a user matching the criteriae: %s." % (request))

    bottle.run(app, host=settings.web_address, port=settings.web_port, debug=True)


if __name__ == '__main__':
    dao = finduser.data.Access(settings.db_default_properties, settings.db_dirty_user_refresh)
    plugin_manager = finduser.plugin.Manager(settings.plugins_path)
    for k, v in plugin_manager.get_plugins().items():
        dao.generate_model(k, v.get_schema())
    main(dao, plugin_manager)
