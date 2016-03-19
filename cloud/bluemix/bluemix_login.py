#!/usr/bin/python

# Copyright (c) 2016 Timothy R. Chavez <timrchavez@gmail.com>

# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import subprocess

from ansible.modules.extras.cloud.bluemix.lib import login

DOCUMENTATION = '''
module: bluemix_login
short_description: Log into IBM Bluemix
version_added: "2.0"
author: "Timothy R. Chavez <timrchavez@gmail.com>"
description:
    - Log into IBM Bluemix
requirements:
    - "cf-cli >= 6.13.0"
    - "python >= 2.6"
extends_documentation_fragment: bluemix
'''

EXAMPLES = '''
# Authenticate to Bluemix
- bluemix_login:
    username: timrchavez@gmail.com
    password: XXX
    org: foo
    space: bar
'''


def main():
    argument_spec   = dict(
        api_url     = dict(default="https://api.ng.bluemix.net"),
        username    = dict(required=True),
        password    = dict(required=True),
        org         = dict(required=True),
        space       = dict(required=True),
    )

    module = AnsibleModule(argument_spec)

    api_url = module.params["api_url"]
    username = module.params["username"]
    password = module.params["password"]
    org = module.params["org"]
    space = module.params["space"]

    try:
        if login(username, password, org, space, api_url):
            module.exit_json(changed=False)
        else:
            module.fail_json(msg=("Authentication failed"))
    except subprocess.CalledProcessError as e:
        module.fail_json(msg=e)


from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
