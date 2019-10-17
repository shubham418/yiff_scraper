import requests
import os
import zipfile
import re


# Main function call to get the links for all externally hosted file and download them if available.
# (Sorted by functions only saving the links VS actual downloads.)
def get_hosted_files(soup):
    get_mega(soup)
    get_onedrive(soup)
    get_dropbox(soup)
    get_gdrive(soup)


# Number the filename if it exists already.
def _check_file_exists(filename):
    n = 1
    while filename in os.listdir():
        lst = filename.split('.')
        ext = lst[-1]
        lst = lst[:-1]
        lst.append("({})".format(n))
        temp_name = "".join(lst) + "." + ext
        if temp_name not in os.listdir():
            filename = temp_name
        n += 1
    return filename


# Get all links to Dropbox on this page and try to download them.
def get_dropbox(soup):
    print('Getting Dropbox links..')
    links = []
    for link in soup.findAll('a'):
        this_link = link.get('href')
        if 'dropbox' in str(this_link).lower():
            links.append(str(this_link).replace('http://https://', 'https://', 1))  # http://https:// sometimes seems to happen?
    for dropbox_url in links:
        try:
            _dl_file(dropbox_url.split('?')[0] + '?dl=1')
        except Exception as e:
            with open('dropbox.txt', 'a+') as f:
                f.write('Could not get file ' + dropbox_url + '. Exception: ' + str(e) + '\n')
                f.close()
    return links


# Get all links to MS OneDrive and save them to a text file.
# TODO Actually download files the links point to.
def get_onedrive(soup):
    print('Getting OneDrive links..')
    links = []
    for link in soup.findAll('a'):
        this_link = link.get('href')
        if any(linkpart in str(this_link).lower() for linkpart in ['live', 'onedrive', '1drv.ms']):
            links.append(str(this_link))
    with open('OneDrive.txt', 'a+') as file:
        for this_url in links:
            file.write(str(this_url) + '\n')
    file.close()


# Get all links to Google Drive and try to download them.
def get_gdrive(soup):
    print('Getting Google Drive links..')
    links = []
    for link in soup.findAll('a'):
        this_link = link.get('href')
        if 'drive.google' in str(this_link).lower(): links.append(str(this_link))
    for google_drive_url in links:
        try:
            _dl_file('https://drive.google.com/uc?export=download&id=' + google_drive_url.split('/')[5])
        except Exception as e:
            with open('gdrive.txt', 'a+') as file:
                file.write(str(google_drive_url) + '\n')
                file.close()
    return links


# Get all links to MEGA and save them to a file.
# TODO Actually download the files the links point to.
def get_mega(soup):
    print('Getting MEGA links..')
    links = []
    for link in soup.findAll('a'):
        this_link = link.get('href')
        if 'mega.nz' in str(this_link).lower(): links.append(str(this_link))
    with open('mega.nz.txt', 'a+') as file:
        for this_url in links:
            file.write(str(this_url) + '\n')
    file.close()


# Unzip any .zip file.
def _unzip_dl(filename, remove_file=False):
    try:
        extract_folder = filename.rstrip('.zip')
        os.mkdir(extract_folder)
        with zipfile.ZipFile(filename, 'r') as zip_file:
            zip_file.extractall(extract_folder)
        zip_file.close()
        if remove_file:
            os.remove(filename)
    except Exception as e:
        with open('unzip.log', 'a+') as f:
            f.write(str(e) + '\n')
            f.close()


# Download a file with automatic naming.
def _dl_file(url):
    download = requests.get(url, allow_redirects=True)
    try:
        filename = re.findall('filename=(.+);', download.headers.get('content-disposition'))[0].strip('\"')
    except:
        print('WARNING: Could not get filename from html headers. Using fallback..')
        filename = 'file'
        with open('downloads.log', 'a+') as file:
            file.write(str(url) + '\n')
            file.close()
    filename = _check_file_exists(filename)
    print('Downloading ' + url + ' to ./' + filename)
    file = open(filename, 'w+b')
    file.write(download.content)
    file.close()
    if filename.lower().endswith('.zip'):
        _unzip_dl(filename=filename, remove_file=True)
