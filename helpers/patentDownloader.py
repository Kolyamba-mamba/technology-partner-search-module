import requests
import os
from bs4 import BeautifulSoup as BS


def urls_saver(args, url):
    filename = args.path + 'urls.txt'
    for year in range(2010, 2021):
        year_url = url + str(year) + "/"
        req = requests.get(year_url)
        html = BS(req.content, 'html.parser')

        tr = html.findChildren('tr')
        tr.pop(0)
        if os.path.isfile(filename):
            mode = 'a'
        else:
            mode = 'w'
        with open(filename, mode) as urls:
            for td in tr:
                href = td.contents[0].text
                download_url = year_url + href
                urls.write(download_url + '\n')
    return filename


def downloader(args, url):
    filename = url[url.rfind('/') + 1:]
    successPath = args.path + 'success.txt'
    errorPath = args.path + 'error.txt'
    if os.path.isfile(successPath):
        with open(successPath) as sp:
            success = sp.readlines()
            if url + '\n' in success:
                return

    try:
        r = requests.get(url, stream=True)
        print(f"Загрузка {url}")

        with open(args.path + filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        with open(successPath, 'a') as success_txt:
            success_txt.write(url + '\n')
        print(f"Загрузка {url} прошла успешно")
    except:
        with open(errorPath, 'a') as error_txt:
            error_txt.write(str(url) + '\n')
        print(f"Ошибка при загрузке {url}")


def main(args):
    url = 'https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/'
    if not os.path.isdir(args.path):
        os.makedirs(args.path)

    if args.saveUrl:
        file_url = urls_saver(args, url)
    else:
        file_url = args.urlsPath

    try:
        with open(file_url, 'r') as f:
            for line in f:
                downloader(args, line.rstrip('\n'))
    except:
        print('Error')
