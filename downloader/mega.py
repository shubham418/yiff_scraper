import logging

import datetime
import os
import subprocess

from downloader import download, url_patterns

logger = logging.getLogger('mega')


def get_link(link):
    link = link.replace('http://https://', 'https://', 1)
    if link.startswith("!#"):
        link = "https://mega.nz/" + link
    try:
        # print(['wsl', 'megadl', link])
        raw_output = subprocess.run(['wsl', 'megadl', link], check=True).stdout.decode("utf8")
        output_file = ''.join(e for e in raw_output.split("Downloaded ")[1] if 32 <= ord(e) <= 122)# e.isalnum() or ord(e) == 46 or )
        logger.debug('Received MEGA file ' + output_file)
        fname, ext = os.path.splitext(output_file)
        new_output_file = fname + '_' + str(datetime.datetime.now().strftime("%Y-%m-%d__%H_%M_%S_%f")) + ext
        os.rename(output_file, new_output_file)
        download.unpack(new_output_file, remove_file=True)
    except Exception as e:
        logger.error(e)
        download.log_failed_download(link)


def _clean_link(link):
    link = link.replace('http://https://', 'https://', 1)
    if link.startswith("#!"):
        link = "https://mega.nz/" + link
    return link


# Get all links to MEGA and save them to a file.
def get_soup(soup):
    logger.debug('Getting MEGA links..')
    links = []
    for element in soup.strings:
        if any(pattern in str(element).lower() for pattern in url_patterns.mega):
            links.append(_clean_link(element))
    links = list(dict.fromkeys(links))
    logger.debug('Found MEGA links: ' + str(links))
    for link in links:
        get_link(link)
