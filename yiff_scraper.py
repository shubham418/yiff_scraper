import sys
import os
import requests
from bs4 import BeautifulSoup
import threading
import concurrent.futures


# Returns the name of the file
def get_file_name(URL):
    lst = URL.rsplit("/")
    name = lst[-1]
    return name


# Returns list containing all files
def get_links(soup, check_str):
    links = soup.find_all("a")
    unfin_paths = []
    for link in links:
        href = link.get("href")
        if href is None:
            continue
        # Check if link is of data
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


# Saves a file from the given URL
# TODO fix no download issue on random files
def save_file(URL):
    name = get_file_name(URL)
    n = 1
    while name in os.listdir():
        lst = name.split(".")
        ext = lst[-1]
        lst = lst[:-1]
        lst.append(f'({n})')
        temp_name = "".join(lst) + "." + ext
        if temp_name not in os.listdir():
            name = temp_name
        n += 1
    print(f"\nDownloading {name} from {URL}")
    in_file = requests.get(URL, stream=True)
    with open(name, "wb") as f:
        for chunk in in_file.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"{name} Complete")


def download_manager(name, links):
    # Create folder to save files
    if name not in os.listdir():
        os.mkdir(name)
    else:
        print("WARNING: Folder for same already exists. Please delete and try again.")
    os.chdir(name)

    download_mode = 0  # 0:standard, 1:threading, 2:pooling

    if download_mode == 0:
        for file_path in links:
            save_file(file_path)

    elif download_mode == 1:
        threads = []
        for file_path in links:
            t = threading.Thread(target=save_file, args=[file_path])
            t.start()
            threads.append(t)
            # save_file(file_path)
        for thread in threads:
            thread.join()

    elif download_mode == 2:
        with concurrent.futures.ThreadPoolExecutor() as executer:
            results = [
                executer.submit(save_file, file_path) for file_path in links
            ]
            for f in concurrent.futures.as_completed(results):
                f.result()

    # return back to execution dir
    os.chdir("..")



# Get all links and download them for the "project"
# TODO implement project updating
def project_links_scraper(URL):
    check_str = ["patreon_data", "patreon_inline"] #strings that indicate content

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
    links = get_links(soup, check_str)

    while curr_page != total_pages:
        curr_page += 1
        payload = {"p": curr_page}
        response = requests.get(URL, params=payload)
        soup = BeautifulSoup(response.content, "html.parser")
        page_element = soup.find_all("p", {"class": "paginate-count"})[0].text
        curr_page = int(page_element.split("/")[0])
        total_pages = int(page_element.split("/")[1])

        links += get_links(soup, check_str)
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
