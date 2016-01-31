#!/usr/bin/env python

# The name of the data file being used
db_name = 'users.sqlite'
# How many seconds until we may refresh dirty users
dirty_user_refresh = 300
# The executable that the batch job must run against
find_user_exec = "python simulate.py"
# This is what we assume by default the messages received are encoded in
default_encoding = "utf8"
