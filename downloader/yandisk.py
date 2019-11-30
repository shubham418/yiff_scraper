# based on https://lowvoltage.github.io/2017/07/29/Yadisk-Direct-Download-Python

import logging
import requests
from downloader import download, url_patterns

logger = logging.getLogger('Yandisk')

API_ENDPOINT = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'


def _get_real_direct_link(sharing_link):
    pk_request = requests.get(API_ENDPOINT.format(sharing_link))

    # Returns None if the link cannot be "converted"
    return pk_request.json().get('href')


def _extract_filename(direct_link):
    for chunk in direct_link.strip().split('&'):
        if chunk.startswith('filename='):
            return chunk.split('=')[1]
    return None


def download_yadisk_link(sharing_link, filename=None):
    direct_link = _get_real_direct_link(sharing_link)
    if direct_link:
        # Try to recover the filename from the link
        filename = filename or _extract_filename(direct_link)

        download = requests.get(direct_link)
        with open(filename, 'wb') as out_file:
            out_file.write(download.content)
        print('Downloaded "{}" to "{}"'.format(sharing_link, filename))
    else:
        print('Failed to download "{}"'.format(sharing_link))


def get_link(link):
    download.download(_get_real_direct_link(link))


# Get all links to Yandex (Yandisk, yadi.sk) and save them to a file.
def get_soup(soup):
    logger.debug('Getting Yandi.sk links..')
    links = []
    for link in soup.findAll('a'):
        this_link = link.get('href')
        if any(pattern in str(this_link).lower() for pattern in url_patterns.yandisk):
            links.append(this_link)
    links = list(dict.fromkeys(links))
    logger.debug('Found yandex links: ' + str(links))
    for link in links:
        download.download(_get_real_direct_link(link))
