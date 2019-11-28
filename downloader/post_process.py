import logging

import os
import subprocess

logger = logging.getLogger("post-process")


def _get_os(cmd):
    if os.name == 'nt':
        process_cmd = ['wsl']
    else:
        process_cmd = []
    return process_cmd + cmd


def _clean_fdupes(folder="."):
    logger.info(subprocess.check_output(
        _get_os(["fdupes", "-Srd", "--noprompt", folder])
    ).decode("utf8"))


def _clean_empty_folders(folder="."):
    logger.debug(subprocess.check_output(
        _get_os(["find", folder, "-type", "d", "-empty"])
    ).decode("utf8"))
    logger.info(subprocess.check_output(
        _get_os(["find", folder, "-type", "d", "-empty", "-delete"])
    ).decode("utf8"))


def cleanup(folder="."):
    _clean_fdupes(folder)
    _clean_empty_folders(folder)

if __name__ == '__main__':
    cleanup()
