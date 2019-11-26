import logging
import requests

from downloader import download, url_patterns

logger = logging.getLogger('gdrive')


def get_link(link):
    download_file_from_google_drive(_get_id(link))


# https://stackoverflow.com/questions/25010369/wget-curl-large-file-from-google-drive
#def download_file_from_google_drive(id, destination):
def download_file_from_google_drive(id):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    #save_response_content(response, destination)
    fname = download.get_filename(response)
    save_response_content(response, fname)
    download.unpack(fname)


def _get_id(link):
    if "open?id=" in link:  # link looks like https://drive.google.com/open?id={ID}
        return link.split('?id=', 1)[1]
    else:  # link looks like https://drive.google.com/file/d/{}/view?usp=sharing
        return link.split('/')[5]


# Get all links to Google Drive and try to download them.
def get_soup(soup):
    logger.debug('Getting google drive links..')
    ids = []
    for link in soup.findAll('a'):
        this_link = link.get('href')
        if any(pattern in str(this_link).lower() for pattern in url_patterns.googledrive):
            ids.append(this_link)
    ids = list(dict.fromkeys(ids))  # remove duplicates
    logger.debug('Found gdrive ids: ' + str(ids))
    for id in ids:
        try:
            download_file_from_google_drive(_get_id(id))
        except:
            download.log_failed_download("https://drive.google.com/uc?export=download&id=" + id)
