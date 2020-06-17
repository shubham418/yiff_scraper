import sys
import os
import requests
from bs4 import BeautifulSoup


# Returns the name of the file
def get_file_name(URL):
    lst = URL.rsplit("/")
    name = lst[-1]
    return name


# # Gets the origin url
# def get_origin(URL):
#     lst = URL.rsplit("/")
#     length = len(lst)
#     lst = lst[2 : (length - 1)]
#     origin = "https://"
#     for x in lst:
#         origin += x
#     return origin


# # Returns list containing all files
# def get_links(soup):
#     tags = soup.find_all("div", {"class":"card-action"})
#     tags = list(map(lambda tag: tag.a.get("href"), tags))
#     return tags

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
# TODO might have to remove as website now provides complete links
# Uses a link list to return a complete list of files
def get_paths(unfinished_lst, origin):
    finished = []
    for x in unfinished_lst:
        if 'http' in x.split('/')[0]:
            finished.append(x)
        else:
            finished.append(origin + x)
    return finished


def new_origin(links):
    good_link = ''
    for x in links:
        if 'http' in x.split('/')[0]:
            good_link = x
            break
    origin = good_link.split('patreon_data')[0]
    return origin

# Saves a file from the given URL
# TODO fix no download issue on random files
def save_file(URL):
    name = get_file_name(URL)
    n = 1
    while name in os.listdir():
        lst = name.split(".")
        ext = lst[-1]
        lst = lst[:-1]
        lst.append("({})".format(n))
        temp_name = "".join(lst) + "." + ext
        if temp_name not in os.listdir():
            name = temp_name
        n += 1
    print("\nDownloading {}".format(name))
    in_file = requests.get(URL, stream=True)
    out_file = open(name, "wb")
    for chunk in in_file.iter_content(chunk_size=8192):
        out_file.write(chunk)
    out_file.close()
    print("{} Complete".format(name))
    print(f'{URL}')


# Get all links and download them for the "project"
# TODO implement project updating
# TODO filter out thumbnails
def download_and_save_all(URL):
    # origin_path = get_origin(URL)
    check_str = ["patreon_data", "patreon_inline"]

    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")
    name_element = soup.find_all("span", {"class": "yp-info-name"})[0].text
    page_element = soup.find_all("p", {"class": "paginate-count"})[0].text
    curr_page = int(page_element.split('/')[0])
    total_pages = int(page_element.split('/')[1])

    print(f"Beginning {name_element}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print("")
    print(f'name: {name_element}\npage: {curr_page}\ntotal pages: {total_pages}')

    # Create folder to save files
    if name_element not in os.listdir():
        os.mkdir(name_element)
    else:
        print("WARNING: Folder for same already exists. Please delete and try again.")

    os.chdir(name_element)

    # from 1st page
    links = get_links(soup, check_str)

    while curr_page != total_pages:
        curr_page += 1
        payload = {'p':curr_page}
        response = requests.get(URL, params=payload)
        soup = BeautifulSoup(response.content, "html.parser")
        page_element = soup.find_all("p", {"class": "paginate-count"})[0].text
        curr_page = int(page_element.split('/')[0])
        total_pages = int(page_element.split('/')[1])

        links += get_links(soup, check_str)
        print(f'Processing page: {page_element}')

    print(f'Number of links: {len(links)}')

    origin_path = new_origin(links)
    final_links = get_paths(links, origin_path)

    for file_path in final_links:
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

    print(
        "\n*******************************************************************************\n"
    )
    print("\nAll projects DONE\n")
    print("\nEnjoy ;)")
