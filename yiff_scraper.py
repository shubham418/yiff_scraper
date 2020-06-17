import sys
import os
import requests
from bs4 import BeautifulSoup
import threading
import concurrent.futures
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool


# Returns the name of the file
def get_file_name(URL):
    lst = URL.rsplit("/")
    name = lst[-1]
    return name


# Returns list containing all files
# filter_types: bl->blacklist, wh->whitelist, None->no_filter
# filter_list example: ['rar', 'jpg']
def get_links(soup, check_str, filter_type=None, filter_list=None):
    links = soup.find_all("a")
    unfin_paths = []
    for link in links:
        href = link.get("href")
        if href is None:
            continue
        # Check if link is of data
        if (filter_type == "bl"):
            if href.split('.')[-1] in filter_list:
                continue
        elif (filter_type == "wh"):
            if href.split('.')[-1] not in filter_list:
                continue
        for string in check_str:
            if string in href:
                unfin_paths.append(href)
                break
    return unfin_paths


# Gets the origin url
def new_origin(links):
    good_link = ""
    for x in links:
        if "http" in x.split("/")[0]:
            good_link = x
            break
    origin = good_link.split("patreon_data")[0]
    return origin


# Uses a link list to return a complete list of files
# TODO might have to remove as website now provides complete links
def get_paths(unfinished_lst):
    origin_path = new_origin(unfinished_lst)
    finished = []
    for x in unfinished_lst:
        if "http" in x.split("/")[0]:
            finished.append(x)
        else:
            finished.append(origin_path + x)
    return finished


def save_file(file_name, URL):
    print(f"\nDownloading {file_name} from {URL}")
    in_file = requests.get(URL, stream=True)
    if in_file.ok:
        with open(file_name, "wb") as f:
            for chunk in in_file.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"{file_name} Complete")


def new_save_file(tuple_):
    file_name, URL = tuple_
    print(f"\nDownloading {file_name} from {URL}")
    in_file = requests.get(URL, stream=True)
    if in_file.ok:
        with open(file_name, "wb") as f:
            for chunk in in_file.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"{file_name} Complete")


# Saves a file from the given URL
# TODO fix no download issue on random files
def save_files(download_dict):
    r_mode = 3  # 0->Linear 1->Normal_threading 2->Threadpool 3->multiprocess

    if r_mode == 1:
        threads = []
        for file_name, URL in download_dict.items():
            t = threading.Thread(target=save_file, args=[file_name, URL])
            t.start()
            threads.append(t)
            # save_file(file_path)
        for thread in threads:
            thread.join()

    elif r_mode == 2:
        with concurrent.futures.ThreadPoolExecutor() as executer:
            results = [
                executer.submit(save_file, file_name, URL)
                for file_name, URL in download_dict.items()
            ]
            for f in concurrent.futures.as_completed(results):
                f.result()

    elif r_mode == 3:
        pool = Pool()
        pool.map(new_save_file, download_dict.items())

    else:
        for file_name, URL in download_dict.items():
            save_file(file_name, URL)


def download_dict_gen(links):
    download_dict = {}  # {filename : url}
    unique_file_names = []
    for url in links:
        name = get_file_name(url)
        n = 1
        while name in unique_file_names:
            lst = name.split(".")
            ext = lst[-1]
            lst = lst[:-1]
            lst.append(f"({n})")
            temp_name = "".join(lst) + "." + ext
            if temp_name not in unique_file_names:
                name = temp_name
            n += 1
        unique_file_names.append(name)
        download_dict[f"{name}"] = url
    return download_dict

def clear_existing_files(download_dict, existing_files):
    cleared_dict = { file_name: download_dict[file_name] for file_name in download_dict if file_name not in existing_files}
    return cleared_dict


def download_manager(name, links):
    # Create folder to save files
    if 'Downloads' not in os.listdir():
        os.mkdir('Downloads')
    os.chdir('Downloads')

    download_dict = download_dict_gen(links)

    if name not in os.listdir():
        os.mkdir(name)
    else:
        print("WARNING: Project already exists, updating has limitations and might not work perfectly.")
        download_dict = clear_existing_files(download_dict, os.listdir(name))

    os.chdir(name)

    # download_dict = download_dict_gen(links)
    save_files(download_dict)

    # return back to execution dir
    os.chdir("../..")


# Get all links and download them for the "project"
# TODO implement project updating
def project_links_scraper(URL):
    check_str = ["patreon_data", "patreon_inline"]  # strings that indicate content
    blacklist_extensions = ["rar", "zip"]
    whitelist_extensions = ["png", "jpg", "gif", "mp4"]
    filter_type='bl'
    filter_list=blacklist_extensions

    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")
    name_element = soup.find_all("span", {"class": "yp-info-name"})[0].text
    page_element = soup.find_all("p", {"class": "paginate-count"})[0].text
    curr_page = int(page_element.split("/")[0])
    total_pages = int(page_element.split("/")[1])

    print(f"Beginning {name_element}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print("")
    print(f"name: {name_element}\npage: {curr_page}\ntotal pages: {total_pages}")

    # from 1st page
    links = get_links(soup, check_str, filter_type=filter_type, filter_list=filter_list)

    while curr_page != total_pages:
        curr_page += 1
        payload = {"p": curr_page}
        response = requests.get(URL, params=payload)
        soup = BeautifulSoup(response.content, "html.parser")
        page_element = soup.find_all("p", {"class": "paginate-count"})[0].text
        curr_page = int(page_element.split("/")[0])
        total_pages = int(page_element.split("/")[1])

        links += get_links(soup, check_str, filter_type=filter_type, filter_list=filter_list)
        print(f"Processing page: {page_element}")

    print(f"Number of links: {len(links)}")

    final_links = get_paths(links)

    download_manager(name_element, final_links)


if __name__ == "__main__":
    projects = sys.argv[1:]
    for project in projects:
        print("\n==========================================================")
        print(f"\n*Starting project {get_file_name(project)}")
        project_links_scraper(project)
        print(f"\n*Project {get_file_name(project)}")

    print(
        "\n*******************************************************************************\n"
    )
    print("\nAll projects DONE\n")
    print("\nEnjoy ;)")
