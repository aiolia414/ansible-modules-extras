#!/usr/bin/python

# Copyright (c) 2016 Timothy R. Chavez <timrchavez@gmail.com>
#
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
import time

from ansible.modules.extras.cloud.bluemix.lib import (
    build_image,
    copy_image,
    find_image,
    remove_image,
)


DOCUMENTATION = '''
module: bluemix_image
short_description: Manage Docker images in IBM Bluemix
version_added: "2.0"
author: "Timothy R. Chavez <timrchavez@gmail.com"
description:
    - Create / destroy a Docker image in IBM Bluemix
requirements:
    - "cf-cli >= 6.13.0"
    - "python >= 2.6"
extends_documentation_fragment: bluemix
'''

EXAMPLES = '''
- name: Upload a Docker image
  bluemix_image:
    state: 'present',
    name: 'foo',
    source: 'my_local_image',
- name: Destroy a Docker image
  bluemix_container:
    state: 'absent'
    name: 'foo'
    wait: true
'''


IMAGE_NAME_RE = ("(?P<namespace>[\w\d]+)?/(?P<name>[\w\d._-]+)"
                 ":(?P<tag>[\w\d._-]+)$")


def main():
    argument_spec   = dict(
        state       = dict(default="present",
                           choices=["absent", "build", "present"]),
        name        = dict(default=None, required=True),
        tag         = dict(default="latest"),
        source      = dict(default=None),
        wait        = dict(default=True, type="bool")
    )

    module = AnsibleModule(argument_spec)

    state = module.params["state"]
    name = module.params["name"]
    tag = module.params["tag"]
    source = module.params["source"]
    wait = module.params["wait"]

    if state == "absent":
        image = find_image(name)
        if image:
            try:
                remove_image(image["id"], tag)
            except subprocess.CalledProcessError as e:
                module.fail_json(msg=e)
            while wait and find_image(image["id"]):
                time.sleep(1)
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)
    elif state == "present":
        try:
            copy_image(name, source, tag)
        except subprocess.CalledProcessError as e:
            module.fail_json(msg=e)
        image = {}
        while wait:
            image = find_image(name)
            if image:
                break
            time.sleep(1)
        if image:
            module.exit_json(changed=True, result=image)
        else:
            module.fail_json(msg="Image could not be found")
    elif state == "build":
        try:
            build_image(name, source, tag)
        except subprocess.CalledProcessError as e:
            module.fail_json(msg=e)
        image = {}
        while wait:
            image = find_image(name)
            if image:
                break
            time.sleep(1)
        if image:
            module.exit_json(changed=True, result=image)
        else:
            module.fail_json(msg="Image could not be found")


from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
