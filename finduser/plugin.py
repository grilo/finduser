#!/usr/bin/env python

import logging
import os
import importlib
import subprocess
import shlex
import json


class Manager:

    def __init__(self, plugins_dir):
        self.plugins_dir = plugins_dir
        self.plugins = {}
        for name, plugin_path in self.scandir().items():
            plugin = self.load_plugin(name, plugin_path)
            if self.plugin_test(plugin):
                logging.info("Successfully loaded plugin: %s" % (plugin.__module__))
                self.plugins[name] = plugin

    def get_plugins(self):
        return self.plugins

    def scandir(self):
        plugins = {}
        for directory in os.listdir(self.plugins_dir):
            if directory.startswith("__"): continue

            plugin_path = os.path.join(self.plugins_dir, directory, 'plugin.py')
            if os.path.isfile(plugin_path):
                plugins[directory] = plugin_path
        if len(plugins.keys()) <= 0:
            logging.warning("No plugins found.")
        return plugins

    def plugin_test(self, plugin):
        if plugin is None: return False
        errors = 0
        try:
            getattr(plugin, 'get_schema')
        except AttributeError:
            errors += 1
            logging.error("Unable to find 'get_schema' method. (%s)" % (errors, plugin.__name__))
        try:
            getattr(plugin, 'run')
        except AttributeError:
            errors += 1
            logging.error("Unable to find 'run' method. (%s)" % (errors, plugin.__name__))

        if errors > 0: return False
        return True

    def load_plugin(self, name, path):
        try:
            module = importlib.machinery.SourceFileLoader(name, path).load_module()
            try:
                return getattr(module, 'Find')()
            except AttributeError:
                logging.error("Unable to find a 'Find' class.")
                return None
        except ImportError as e:
            logging.error("Unable to load plugin: %s" % (path))
            return None

    def find_all(self, personId):
        results = {}
        for name, plugin in self.plugins.items():
            results[name] = plugin.run(personId)
        return personId, results


class Plugin:

    def __init__(self):
        self.command = None

    def get_schema(self):
        raise NotImplementedError

    def validate_json(self, json_obj):
        errors = 0
        for k, v in self.get_schema().items():
            if k not in json_obj.keys():
                logging.error("Missing data. expected key (%s) to exist in (%s)." % (k, json_obj))
                error += 1
            if v == 'str' and type(json_obj[k]) == str: continue
            elif v == 'int' and type(json_obj[k]) == int: continue
            elif v == 'float' and type(json_obj[k]) == float: continue
            elif v == 'date' and type(json_obj[k]) == float: continue
            elif v == 'bool' and json_obj[k] == True or json_obj[k] == False: continue
            else:
                logging.error("Invalid data: value (%s) has type (%s) but I expected (%s)." % (json_obj[k], type(json_obj[k]), v))
                error += 1

        if errors > 0:
            return False
        return True


    def run(self, personId):
        """Execute a CLI utility and return the results.

        This is the meat of the find user. Since Python has much poorer drivers
        for esoteric stuff than Java, we simply created a very small CLI util
        which does the work for us and use Python to glue everything together.

        Args:
            personId (str): A parameter passed to the CLI util (self.command).

        Returns:
            list(dict): The [somewhat altered] JSON output of the utility.
        """
        if self.command is None: raise NotImplementedError

        logging.debug("Retrieving (%s) for user %d" % (self.__class__.__name__, personId))
        cmd = " ".join([self.command, str(personId)])

        try:
            output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            logging.error("Invokation went horribly wrong: %s" % (cmd))
            return []

        results = []
        for json_obj in json.loads(output.decode('utf8')):
            if self.validate_json(json_obj):
                json_obj["user"] = personId
                results.append(json_obj)
        logging.debug("Retrieved (%d) results for user (%s)" % (len(results), personId))
        return results

