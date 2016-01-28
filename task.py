#!/usr/bin/env python

import logging
import subprocess
import shlex


class Async:

    def __init__(self, command):
        self.command = command
        self.__proc = None
        self.finished = False
        self.stdout = None
        self.stderr = None
        self.pid = None
        self.returncode = None

    def start(self):
        self.__proc = subprocess.Popen(shlex.split(self.command), stdout=subprocess.PIPE, universal_newlines=True)
        self.pid = self.__proc.pid

    def kill(self):
        # We don't actually send a SIGKILL since this may cause severe issues
        # with unclosed file descriptors and such.
        return self.__proc.terminate()

    def done(self):
        if self.__proc.poll() is not None:
            self.__proc.wait()
            self.stdout, self.stderr = self.__proc.communicate()
            self.returncode = self.__proc.returncode
            self.finished = True
        return self.finished

    def wait(self):
        self.__proc.wait()
        return self.done()
