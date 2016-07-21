import re

from subprocess import check_output


def bind_ip(ip_address, container_id):
    container = find_container(container_id)
    if container:
        return check_output(
            ["cf", "ic", "ip", "bind", ip_address, container["id"]]).strip()
    return container


def build_image(name, source, tag="latest"):
    name = "{0}:{1}".format(name, tag)
    return check_output(["cf", "ic", "build", "-t", name, source]).strip()


def copy_image(name, source, tag="latest"):
    name = "{0}:{1}".format(name, tag)
    return check_output(["cf", "ic", "cpi", source, name]).strip()


def find_container(container_id):
    output = check_output(["cf", "ic", "ps", "--all", "--no-trunc"])
    for line in output.splitlines()[1:]:
        # FIXME: Add more info
        ports = ""
        try:
            id, image, command, created, status, ports, names = re.split(r"  +", line)
        except ValueError:
            id, image, command, created, status, names = re.split(r"  +", line)
        state = status.lower().split()[0]
        if container_id == id or container_id == names:
            return dict(
                id=id,
                image=image,
                command=command,
                created=created,
                state=state,
                ports=ports,
                names=names
            )
    return {}


def find_ip(ip_address):
    for ip in list_ips(ip_address):
        if ip["address"] == ip_address:
            return ip
    return {}


def find_image(image_id):
    output = check_output(["cf", "ic", "images", "--all", "--no-trunc"])
    for line in output.splitlines()[1:]:
        repo, tag, id = line.split()[:3]
        if repo.endswith(image_id) or image_id == id:
            return dict(repo=repo, tag=tag, id=id)
    return None


def list_ips():
    output = check_output(["cf", "ic", "ip", "list", "--all"])
    records = output.splitlines()
    if len(records) < 3:
        yield {}
    else:
        for record in records[3:]:
            container_id = ""
            try:
                ip_address, container_id = record.split()
            except ValueError:
                ip_address = record
            container = find_container(container_id)
            yield dict(
                address=ip_address.strip(),
                container=container
            )


def login(username, password, org, space, api_url="https://api.ng.bluemix.net"):
    return check_output(
        ["cf", "login", "-a", api_url, "-u", username, "-p", password,
         "-o", org, "-s", space])


def  push_image(src, tag="latest"):
    image_id = "{0}:{1}".format(src, tag)
    return check_output(["docker", "push", src])


def remove_image(image_id, tag="latest"):
    image_id = "{0}:{1}".format(image_id, tag)
    return check_output(["cf", "ic", "rmi", image_id])


def  release_ip(ip_address):
    ip = find_ip(ip_address)
    if ip:
        return check_output(["cf", "ic", "ip", "release", ip["address"]])
    return ip


def request_ip(reuse=False):
    if reuse:
        for ip in list_ips():
            if not ip["container"]:
                return dict(ip=ip["address"]), False
    output = map(
        str.strip, check_output(["cf", "ic", "ip", "request"]).splitlines())
    if output[0] == "OK":
        m = re.search(
            "IP address \"(?P<ip>\d+.\d+.\d+.\d+)\" was obtained.",  output[1])
        if m:
            return dict(ip=m.group("ip")), True
    else:
        return {}


def rm(container_id):
    return check_output(["cf", "ic", "rm", "-f", container_id]).strip()


def run(name, ports, memory, envvars, links, volumes, image_id,
        command, detach):
    cmd = ["cf", "ic", "run"]
    if name:
        cmd.append("--name")
        cmd.append(name)
    if ports:
        for port in ports:
            cmd.append("--publish")
            cmd.append(str(port))
    if memory:
        cmd.append("--memory")
        cmd.append(str(memory))
    if envvars:
        for envvar in envvars:
            cmd.append("-e")
            cmd.append(envvar)
    if links:
        for link in links:
            cmd.append("--link")
            cmd.append(str(link))
    if volumes:
        for volume in volumes:
            cmd.append(str("--volume"))
            cmd.append(volume)
    if detach:
        cmd.append("--detach")
    image = find_image(image_id)
    if image:
        cmd.append(image["repo"])
    if command:
        for component in command.strip().split():
            cmd.append(component.strip())
    return check_output(cmd).strip()


def unbind_ip(ip_address, container_id):
    container = find_container(container_id)
    if container:
        return check_output(
            ["cf", "ic", "ip", "unbind", ip_address, container["id"]]).strip()
    return {}
