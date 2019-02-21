import sys, os
import requests
from bs4 import BeautifulSoup

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
def get_links(URL, check_str):
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all('a')
    unfin_paths = []
    for link in links:
        href = link.get('href')
        if href is None:
            continue
        # Check if link is of data
        if check_str in href:
            unfin_paths.append(href)
    return unfin_paths

# Uses a link list to return a complete list of files
def get_paths(unfinished_lst, origin):
    finished = []
    for x in unfinished_lst:
        finished.append(origin+x)
    return finished

# Saves a file from the given URL
def save_file(URL):
    name = get_file_name(URL)
    print("\nDownloading {}".format(name))
    in_file = requests.get(URL, stream=True)
    out_file = open(name, 'wb')
    for chunk in in_file.iter_content():
        out_file.write(chunk)
    print("\n{} Complete".format(name))

# Get all links and download them for the "project"
def download_and_save_all(URL):
    origin_path = get_origin(URL)
    origin_name = get_file_name(URL)
    check_str = "patreon_data"

    # Create folder to save files
    if origin_name not in os.listdir():
        os.mkdir(origin_name)
    else:
        print("WARNING: Folder for same already exists. Please delete and try again.")

    # Change to folder to save files
    os.chdir(origin_name)

    links = get_paths(get_links(URL, check_str), origin_path)

    for file_path in links:
        save_file(file_path)

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
