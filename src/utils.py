import os
import subprocess


def run_command_and_get_output(command: list[str]) -> tuple[str, str]:
    if is_flatpak():
        if command[0] != "flatpak-spawn":
            from distrobox_handler import FLATPAK_SPAWN_ARR

            command = [*FLATPAK_SPAWN_ARR, *command]

    output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print("running", command)

    return output.stdout.decode("utf-8"), output.stderr.decode("utf-8")


def detect_terminal() -> tuple[str, str]:
    terminal = "gnome-terminal"
    terminal_exec_arg = "--"
    err = run_command_and_get_output(["which", "gnome-terminal"])[1]

    if err:
        terminal = "konsole"
        terminal_exec_arg = "-e"

    return terminal, terminal_exec_arg


def is_flatpak() -> bool:
    """
    Detects if running as flatpak
    """
    f = os.getenv("FLATPAK_ID")

    if f:
        return True

    if os.path.exists("/.flatpak-info"):
        return True

    return False


def get_distro_img(distro: str):
    """
    Gets icon for provided distro
    """
    distro_colours = {
        "ubuntu": "#FF4400",
        "debian": "#da5555",
        "centos": "#ff6600",
        "oracle": "#ff0000",
        "fedora": "blue",
        "arch": "#12aaff",
        "alma": "#dadada",
        "slackware": "#6145a7",
        "gentoo": "#daaada",
        "kali": "#000000",
        "alpine": "#2147ea",
        "clearlinux": "#56bbff",
        "void": "#abff12",
        "amazon": "#de5412",
        "rocky": "#91ff91",
        "redhat": "#ff6662",
        "opensuse": "#daff00",
        "mageia": "#b612b6",
    }

    colour = distro_colours[distro] if distro in distro_colours else "#000000"

    return f"<span foreground='{colour}'>⬤</span>"


def has_distrobox_installed() -> bool:
    """
    Returns whether `which` can find distrobox
    """
    cmd = ["which", "distrobox"]
    if is_flatpak():
        cmd = ["flatpak-spawn", "--host", "which", "distrobox"]

    out, err = run_command_and_get_output(cmd)

    # Fedora's behaviour
    if "no distrobox in" in out or "no distrobox in" in err:
        return False

    # Debian's behaviour
    if not out and not err:
        return False

    return True
