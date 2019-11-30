#!/usr/local/bin/python3.6

import sys
import requests
from bs4 import BeautifulSoup
from downloader import download, post_process

import logging
import os

if not os.path.isfile('yiff_scraper.log'): open('yiff_scraper.log', 'a+').close()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s *%(levelname)s* %(name)s in %(filename)s.%(funcName)s: %(message)s',
                    handlers=[logging.FileHandler('yiff_scraper.log', mode='a'), logging.StreamHandler()])


def _get_pages(soup):
    html_pages = soup.find("p", class_="paginate-count")
    if html_pages:
        split_pages = html_pages.get_text().split(" / ")
        return int(split_pages[0]), int(split_pages[1])
    else:
        return 1, 1


# Returns the name of the file
def get_file_name(URL):
    lst = URL.rsplit('/')
    name = lst[-1]
    return name


# Gets the origin url
def get_origin(URL):
    lst = URL.rsplit('/')
    length = len(lst)
    lst = lst[2:(length-1)]
    origin = "https://"
    for x in lst:
        origin += x
    return origin


# Returns list containing all files
def get_links(soup, check_str):
    links = soup.find_all('a')
    unfin_paths = []
    for link in links:
        href = link.get('href')
        if href is None:
            continue
        # Check if link is of data
        for string in check_str:
            if string in href:
                unfin_paths.append(href)
                break
    return unfin_paths


# Uses a link list to return a complete list of files
def get_paths(unfinished_lst, origin):
    finished = []
    for x in unfinished_lst:
        finished.append(origin+x)
    return finished


# Saves a file from the given URL
# TODO fix no download issue on random files
def save_file(URL):
    name = get_file_name(URL)
    n = 1
    while name in os.listdir():
        lst = name.split('.')
        ext = lst[-1]
        lst = lst[:-1]
        lst.append("({})".format(n))
        temp_name = "".join(lst) + "." + ext
        if temp_name not in os.listdir():
            name = temp_name
        n += 1
    print("\nDownloading {}".format(name))
    response = requests.get(URL, stream=True)
    with open(name, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    print("\n{} Complete".format(name))
    download.unpack(filename=name, remove_file=True)


# Get all links and download them for the "project"
# TODO implement project updating
# TODO filter out thumbnails
def download_and_save_page(soup, check_str, origin_path):
    download.get_soups(soup)

    links = get_paths(get_links(soup, check_str), origin_path)

    for file_path in links:
        try:
            save_file(file_path)
        except Exception as e:
            print('ERROR: Could not save ' + file_path + '. Exception: ' + str(e))


def download_and_save_all(URL):
    origin_path = get_origin(URL)  # broken
    origin_path = 'https://yiff.party/'
    check_str = ["patreon_data", "patreon_inline"]

    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")
    name_element = soup.find_all('span', {"class": "yp-info-name"})[0].string
    print("*" + name_element)

    # Create folder to save files
    if name_element not in os.listdir():
        os.mkdir(name_element)
    else:
        print("WARNING: Folder for same already exists. Please delete and try again.")

    os.chdir(name_element)

    download_and_save_page(soup, check_str, origin_path)  # save this page

    if not "p=" in URL:  # particular page number selected, only download single page
        for page in range(2, _get_pages(soup)[1]+1, 1):  # go with each page
            page_url = URL.rsplit("?", 1)[0] + "?p=" + str(page)
            page_soup = BeautifulSoup(requests.get(page_url).content, "html.parser")
            print("Saving "+ name_element + "page " + str(page))
            download_and_save_page(page_soup, check_str, origin_path)

    try:
        post_process.cleanup()
    except:
        print("WARNING: Couldn't cleanup.")

    # return back to execution dir
    os.chdir("..")


if __name__ == "__main__":
    projects = sys.argv[1:]
    for project in projects:
        print("\n==========================================================")
        print("\n*Starting project {}".format(get_file_name(project)))
        download_and_save_all(project)
        print("\n*Project {} done".format(get_file_name(project)))

    print("\n*******************************************************************************\n")
    print("\nAll projects DONE\n")
    print("\nEnjoy ;)")
