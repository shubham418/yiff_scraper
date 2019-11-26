
import os
import subprocess


def _get_wsl(cmd):
    if os.name == 'nt':
        process_cmd = ['wsl']
    else:
        process_cmd = []
    return process_cmd + cmd


def _clean_fdupes(folder="."):
    print(subprocess.check_output(
        _get_wsl(["fdupes", "-Srd", "--noprompt", folder])
    ).decode("utf8"))


def _clean_empty_folders(folder="."):
    print(subprocess.check_output(
        _get_wsl(["find", folder, "-type", "d", "-empty"])
    ).decode("utf8"))
    print(subprocess.check_output(
        _get_wsl(["find", folder, "-type", "d", "-empty", "-delete"])
    ).decode("utf8"))


def cleanup(folder="."):
    _clean_fdupes(folder)
    _clean_empty_folders(folder)