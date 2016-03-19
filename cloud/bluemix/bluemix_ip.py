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


from ansible.modules.extras.cloud.bluemix.lib import (
    find_ip,
    release_ip,
    request_ip,
)

DOCUMENTATION = '''
module: bluemix_ip
short_description: Create / destroy a floating IP in IBM Bluemix
version_added: "2.0"
author: "Timothy R. Chavez <timrchavez@gmail.com"
description:
    - Create / destroy a floating IP in IBM Bluemix
requirements:
    - "cf-cli >= 6.13.0"
    - "python >= 2.6"
extends_documentation_fragment: bluemix
'''

EXAMPLES = '''
- name: Create a floating IP
  bluemix_ip:
    state: 'present'
- name: Destroy a floating IP
  bluemix_ip:
    state: 'absent'
    ip_address: '1.2.3.4'
'''


def main():
    argument_spec   = dict(
        state       = dict(default="present", choices=["absent", "present"]),
        reuse       = dict(default=False, type="bool"),
        ip_address  = dict(default=None)
    )

    module = AnsibleModule(argument_spec)

    state = module.params["state"]
    reuse = module.params["reuse"]
    ip_address = module.params["ip_address"]

    if state == "present":
        ip, reused = request_ip(reuse)
        if ip:
            module.exit_json(changed=reused, result=ip)
        else:
            module.fail_json(msg="Could not allocate IP")
    else:
        ip = find_ip(ip_address)
        if ip:
            release_ip()
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)


from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
