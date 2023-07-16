import os
import subprocess


def run_command_and_get_output(command: list[str]) -> tuple[str, str]:
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

    return False


def get_imgs_dir() -> str:
    """
    Returns local imgs dir if local, else XDG_DATA
    """
    imgs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if is_flatpak():
        imgs_dir = os.getenv("XDG_DATA_HOME")

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
