import os, subprocess


def dlPages(creator_id, page_end, page_start=1, base_url='https://yiff.party/patreon/'):
    args = []
    for page in range(page_start, page_end+1, 1):
        args.append(base_url + str(creator_id) + '?p=' + str(page))
    return args


cmd = ['python', os.path.join('.', 'yiff_scraper.py')]

cmd.extend(dlPages(creator_id=946301, page_end=10))

subprocess.call(cmd)
