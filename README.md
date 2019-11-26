# yiff_scraper
Scrapes off all content from a yiff.party page.

# Requirements:
**Python 3** 
```
pip install -r requirements.txt
```
**fdupes** _Used for cleanup after downloading._
```
apt install fdupes
```
**megatools** _Downloading files from mega.nz._
```
apt install megatools
```
**Subsystem for Linux** _If you want to clean up and download from mega.nz on Windows._
```
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
```

# Usage:
1. Open the shell
2. Run the following command replacing {links} with your urls:
```
python yiff_scraper.py {link 1} {link 2} {any number of links}
```
_You may pass a page number within the link `?p=` to download a single page only (e.g. just updating from first page)._

## External Files:
The script will download files from if they are linked on the respective page
* https://dropbox.com
* https://drive.google.com/
* https://mega.nz/
* https://onedrive.live.com/
* https://disk.yandex.com