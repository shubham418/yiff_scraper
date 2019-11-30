import logging

import os
import subprocess

from downloader import download

logger = logging.getLogger("post-process")


def _clean_fdupes(folder="."):
    logger.info(subprocess.check_output(
        download.get_os_cmd(["fdupes", "-Srd", "--noprompt", folder])
    ).decode("utf8"))


def _clean_empty_folders(folder="."):
    logger.debug(subprocess.check_output(
        download.get_os_cmd(["find", folder, "-type", "d", "-empty"])
    ).decode("utf8"))
    logger.info(subprocess.check_output(
        download.get_os_cmd(["find", folder, "-type", "d", "-empty", "-delete"])
    ).decode("utf8"))


def cleanup(folder="."):
    _clean_fdupes(folder)
    _clean_empty_folders(folder)


if __name__ == '__main__':
    cleanup()
