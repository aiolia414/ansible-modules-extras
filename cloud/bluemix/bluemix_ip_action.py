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

from ansible.modules.extras.cloud.bluemix.lib import (
    bind_ip,
    unbind_ip
)

DOCUMENTATION = '''
module: bluemix_ip_action
short_description: Create / destroy an IBM Bluemix container
version_added: "2.0"
author: "Timothy R. Chavez <timrchavez@gmail.com>"
description:
    - Create / destroy an IBM Bluemix container
requirements:
    - "cf-cli >= 6.13.0"
    - "python >= 2.6"
extends_documentation_fragment: bluemix
'''

EXAMPLES = '''
- name: Bind IP address
  bluemix_ip_action:
    action: 'bind',
    ip_address: '1.2.3.4',
    container: '165f48ef-967',
- name: Unbind IP address
  bluemix_ip_action:
    action: 'unbind',
    ip_address: '1.2.3.4'
'''


def main():
    argument_spec   = dict(
        action      = dict(required=True, choices=["bind", "unbind"]),
        ip_address  = dict(required=True),
        container   = dict(default=None)
    )

    module = AnsibleModule(argument_spec)

    action = module.params["action"]
    ip_address = module.params["ip_address"]
    container = module.params["container"]

    if action == "bind":
        try:
            bind_ip(ip_address, container)
        except subprocess.CalledProcessError as e:
            module.fail_json(msg=e)
        else:
            module.exit_json(changed=True)
    elif action == "unbind":
        try:
            unbind_ip(ip_address)
        except subprocess.CalledProcessError as e:
            module.fail_json(msg=e)
        else:
            module.exit_json(changed=True)


from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
