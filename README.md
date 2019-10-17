# yiff_scraper
Scrapes off all content from a yiff.party page

# Requirements:
1. Python 3
2. Requests
3. beautifulsoup4

To install python3 follow online instructions.
To install the dependencies:
```
pip install -r requirements.txt
```

# Usage:
1. Open the shell
2. Run the following command replacing {links} with your url's:
```
python yiff_scraper.py {link 1} {link 2} {any number of links}
```
# External Files:
The script will look for links to
 - https://dropbox.com
 - https://drive.google.com/
 - https://mega.nz/ - only saves links to text file. Can download via `megadl` cli:
```
while read link; do
  megadl "$link"
done < "./mega.nz.txt"
```
 - https://onedrive.live.com/ - only saves links to text file `OneDrive.txt`