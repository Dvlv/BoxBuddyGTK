import os
import subprocess


def run_command_and_get_output(command: list[str]) -> tuple[str, str]:
    if is_flatpak():
        if command[0] != "flatpak-spawn":
            from distrobox_handler import FLATPAK_SPAWN_ARR

            command = [*FLATPAK_SPAWN_ARR, *command]

    output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("running", command)

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


def get_imgs_dir() -> str:
    """
    Returns local imgs dir if local, else XDG_DATA
    """
    imgs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    return os.path.join(imgs_dir, "imgs")


def get_distro_img(distro: str):
    """
    Gets path to icon for provided distro
    """
    imgs_dir = get_imgs_dir()
    img_filename = distro + ".png"

    img_fullpath = os.path.join(imgs_dir, img_filename)
    if os.path.exists(img_fullpath):
        return img_fullpath

    img_filename = distro + ".svg"
    img_fullpath = os.path.join(imgs_dir, img_filename)

    if os.path.exists(img_fullpath):
        return img_fullpath

    return ""


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
