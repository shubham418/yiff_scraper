# https://docs.microsoft.com/en-us/onedrive/developer/rest-api/api/shares_get?view=odsp-graph-online

import requests
import os

import logging

from downloader import download, url_patterns

logger = logging.getLogger('OneDrive')


def _get_id(link_id):
    if not link_id.lower().startswith("https://"):
        return link_id  # id only
    linkparts = link_id.split("/")
    for i in range(0, len(linkparts)):
        if linkparts[i] == "1drv.ms" and len(linkparts[i+1]) == 1:
            return linkparts[i+2].rsplit("?", 1)[0]  # id from link
    return ""  # no id found


def _get_driveitem(link, base_url="https://api.onedrive.com/v1.0/shares/"):
    response = requests.get(base_url + _get_id(link) + "/driveItem/?$expand=children")
    return response.json()


def _get_download_item(driveItem, folder=""):
    logger.debug("Adding " + driveItem["name"])
    return {
        "fdir": folder,
        "fname": driveItem["name"],
        "downloadUrl": driveItem["@content.downloadUrl"]
    }


def _get_content(link, folder=""):
    driveItem = _get_driveitem(link)
    contents = []
    children = []
    if "folder" in driveItem:
        folder = os.path.join(folder, driveItem["name"])
    if "@content.downloadUrl" in driveItem:
        contents.append(_get_download_item(driveItem, folder))
    if "children" in driveItem:
        for child in driveItem["children"]:
            if "@content.downloadUrl" in child:
                contents.append(_get_download_item(child, folder))
            if "folder" in child:
                children.append(child["webUrl"])
    logger.info('Found ' + str(len(children)) + ' child items and ' + str(len(contents)) + ' content downloads in ' + link)
    logger.debug("Children: " + str(children))
    logger.debug("Contents: " + str(contents))
    if children:
        for child in children:
            recursive_contents, recursive_children = _get_content(child, folder)
            contents.extend(recursive_contents)
    return contents, children


def get_link(link):
    content = _get_content(link)[0]
    for item in content:
        logger.debug("Downloading " + str(item))
        download.download(
            url=item["downloadUrl"],
            fname=os.path.join(item["fdir"], item["fname"])
        )


# Get all links to MS OneDrive and save them to a text file.
def get_soup(soup):
    links = []
    for link in soup.findAll('a'):
        this_link = link.get('href')
        if any(pattern in str(this_link).lower() for pattern in url_patterns.onedrive):
            links.append(str(this_link))
    links = list(dict.fromkeys(links))
    logger.debug('Found onedrive links: ' + str(links))
    for link in links:
        get_link(link)
