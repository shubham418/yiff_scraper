import logging

from downloader import download, url_patterns

logger = logging.getLogger('dropbox')


def get_link(link):
    return link.split('?')[0] + '?dl=1'


# Get all links to Dropbox on this page and try to download them.
def get_soup(soup):
    logger.debug('Getting dropbox links..')
    links = []
    for link in soup.findAll('a'):
        this_link = link.get('href')
        if any(pattern in str(this_link).lower() for pattern in url_patterns.dropbox):
            #logger.debug('Found dropbox link: ' + str(this_link))
            links.append(this_link)
    links = list(dict.fromkeys(links))
    logger.debug('Found dropbox links: ' + str(links))
    for link in links:
        download.download(get_link(link))
