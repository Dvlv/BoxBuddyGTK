import subprocess


def run_command_and_get_output(command: list[str]) -> tuple[str, str]:
    output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return output.stdout.decode("utf-8"), output.stderr.decode("utf-8")


def detect_terminal() -> tuple[str, str]:
    terminal = "gnome-terminal"
    terminal_exec_arg = "--"
    err = run_command_and_get_output(["which", "gnome-terminal"])[1]

    if err:
        terminal = "konsole"
        terminal_exec_arg = "-e"

    return terminal, terminal_exec_arg
