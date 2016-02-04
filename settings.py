#!/usr/bin/env python

# This is what we assume by default the messages received are encoded in
default_encoding = "utf8"
log_format = '%(asctime)s::%(levelname)s::%(message)s'
log_level = 'INFO'

# data.py
# The name of the data file being used
db_name = 'users.sqlite'
# How many seconds until we may refresh dirty users
db_dirty_user_refresh = 300
# Default parameters which will be inserted automatically in the query
# unless explicitly overriden by the user
db_default_properties = {
    "product": {
        "accBlocked": False
    }
}

# web.py
web_address = '0.0.0.0'
web_port = 8080

# batch.py
batch_default_workers = 16
# The executable that the batch job must run against
batch_find_user_exec = "python simulate.py"
