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
    find_container,
    rm,
    run
)

DOCUMENTATION = '''
module: bluemix_container
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
- name: Create a container
  bluemix_container:
    state: 'present',
    name: 'foo',
    image: 'ibmnode',
- name: Destroy a container
  bluemix_container:
    state: 'absent'
    name: 'foo'
'''


def main():
    argument_spec   = dict(
        state       = dict(default="present", choices=["absent", "present"]),
        name        = dict(default=None),
        detach      = dict(default=True),
        memory      = dict(default=256, choices=[64, 256, 512, 1024, 2048]),
        env         = dict(default=None, type="list"),
        links       = dict(default=None, type="list"),
        volumes     = dict(default=None, type="list"),
        ports       = dict(default=None, type="list"),
        command     = dict(default=None),
        image       = dict(default="ibmnode"),
        wait        = dict(default=False, type="bool")
    )

    module = AnsibleModule(argument_spec)

    state = module.params["state"]
    name = module.params["name"]
    detach = module.params["detach"]
    memory = module.params["memory"]
    env = module.params["env"]
    links = module.params["links"]
    volumes = module.params["volumes"]
    ports = module.params["ports"]
    command = module.params["command"]
    image = module.params["image"]
    wait = module.params["wait"]

    if state == "present":
        container = find_container(name)
        if container:
            module.exit_json(changed=False, result=container)
        else:
            try:
                container_id = run(
                    name, ports, memory, env, links, volumes, image,
                    command, detach)
            except subprocess.CalledProcessError as e:
                module.fail_json(msg=e)
            container = None
            # FIXME: Need timeout
            while wait:
                container = find_container(container_id)
                if container and container["state"] == "running":
                    break
                time.sleep(1)
            module.exit_json(changed=True, result=container)
    else:
        container = find_container(name)
        if not container:
            module.exit_json(changed=False, result=container)
        else:
            try:
                container_id = rm(container["id"])
            except subprocess.CalledProcessError as e:
                module.fail_json(msg=e)
            container = None
            # FIXME: Need timeout
            while wait:
                container = find_container(container_id)
                if not container:
                    break
                time.sleep(1)
            module.exit_json(changed=True, result=container)


from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
