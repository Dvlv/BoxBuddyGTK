import subprocess
from dataclasses import dataclass
from typing import Tuple, List

from utils import detect_terminal, is_flatpak, run_command_and_get_output

FLATPAK_SPAWN = "flatpak-spawn --host " if is_flatpak() else ""
FLATPAK_SPAWN_ARR = ["flatpak-spawn", "--host"] if is_flatpak() else []

fp_spawn = []
if is_flatpak():
    fp_spawn = ["flatpak", "spawn", "--host"]


@dataclass
class Distrobox:
    name: str
    distro: str
    image_url: str
    container_id: str
    status: str


def get_all_distroboxes() -> List[Distrobox]:
    """
    Fetches all distroboxes
    """
    distroboxes = []

    out, err = run_command_and_get_output(
        [*FLATPAK_SPAWN_ARR, "distrobox", "list", "--no-color"]
    )

    if not out:
        return []

    out_lines = out.split("\n")
    if len(out_lines) == 1:
        return []

    for box_line in out.split("\n")[1:]:
        if box_line:
            fields = box_line.split("|")
            if len(fields) > 3:
                distroboxes.append(
                    Distrobox(
                        name=fields[1].strip(),
                        distro=try_parse_disto_name_from_url(fields[3].strip()),
                        image_url=fields[3].strip(),
                        container_id=fields[0].strip(),
                        status=fields[2].strip(),
                    )
                )

    return distroboxes


def try_parse_disto_name_from_url(image_url: str):
    distros = (
        "ubuntu",
        "debian",
        "centos",
        "oracle",
        "fedora",
        "arch",
        "alma",
        "slackware",
        "gentoo",
        "kali",
        "alpine",
        "clearlinux",
        "void",
        "amazon",
        "rocky",
        "redhat",
        "opensuse",
        "mageia",
    )

    distro_name = "zunknown"

    # first check last bit of url, e.g. docker.io/ubuntu:20.04, check the ubuntu bit
    last_part_of_url = image_url.split("/")[-1]

    for d in distros:
        if d in last_part_of_url:
            distro_name = d
            break

    if distro_name != "zunknown":
        return distro_name

    # if we havent matched, check the URL itself, e.g. opensuse.com/leap:15.3
    for d in distros:
        if d in image_url:
            distro_name = d
            break

    return distro_name


def open_terminal_in_box(box_name: str):
    terminal, terminal_exec_arg = detect_terminal()

    subprocess.Popen(
        [
            *FLATPAK_SPAWN_ARR,
            terminal,
            terminal_exec_arg,
            "distrobox",
            "enter",
            box_name,
            "&",
        ]
    )


def run_command_in_box(command: str, box_name: str):
    cmd = [
        *FLATPAK_SPAWN_ARR,
        "distrobox",
        "enter",
        box_name,
        "--",
        *command.split(" "),
    ]

    return run_command_and_get_output(cmd)


def export_app_from_box(box_name: str, app: str):
    cmd = f"distrobox export -a {app}"

    return run_command_in_box(cmd, box_name)


def upgrade_box(box_name: str):
    terminal, terminal_exec_arg = detect_terminal()

    subprocess.Popen(
        [
            *FLATPAK_SPAWN_ARR,
            terminal,
            terminal_exec_arg,
            "distrobox",
            "upgrade",
            box_name,
        ]
    )


def delete_box(box_name: str):
    return run_command_and_get_output(f"distrobox rm {box_name} -f".split(" "))


def create_box(box_name: str, image: str):
    cmd = f"distrobox create -n {box_name} -i {image} -Y 2>&1"

    return run_command_and_get_output(cmd.split(" "))


def init_new_box(box_name: str):
    run_command_and_get_output(f"setsid distrobox enter {box_name} -- ls".split(" "))


def get_available_images():
    out, err = run_command_and_get_output("distrobox create -C".split(" "))

    imgs = []
    if out:
        out_lines = out.split("\n")
        for line in out_lines:
            if line != "Images":
                imgs.append(try_parse_disto_name_from_url(line))

    return sorted(imgs)