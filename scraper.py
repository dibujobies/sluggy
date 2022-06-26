import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import re
import shutil
import requests
import time


def process_img(path, tag):
    title = tag['alt']
    link = tag['data-src'] if 'data:image' in tag['src'] else tag['src']
    comic_date = title.split(' ')[-1].split('/')
    month, day, year = comic_date
    ext = re.search(r'\.[a-zA-Z]+$', link).group(0)
    filename = f'{path}/Comic-for-{year}-{month}-{day}{ext}'
    number = 0
    while os.path.exists(filename):
        number += 1
        filename = f'{path}/Comic-for-{year}-{month}-{day}-{number}{ext}'
    print(link, title, filename)
    cookies = {
        '_ga': 'GA1.2.1778324893.1655873342',
        '_gid': 'GA1.2.532556803.1656173773',
        '_gat': '1',
    }

    headers = {
        'authority': 'static.sluggy.com',
        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://archives.sluggy.com/',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
    }
    response = requests.get(link, headers=headers, cookies=cookies, stream=True)
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def main():
    for i in range(30, 74):
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome('./chromedriver', options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
              """
        })
        path = f'./images/Chapter_{i}'
        if not os.path.isdir(path):
            os.makedirs(path)
        web_temp = f'https://archives.sluggy.com/book.php?chapter={i}#begin'
        driver.get(web_temp)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        images = soup.findAll('img', attrs={'alt': True})
        links = {}
        for index, image in enumerate(images):
            title = image['alt']
            link = image['data-src'] if 'data:image' in image['src'] else image['src']
            links[link] = links.get(link, 0) + 1
            if links[link] > 1 or 'comic for' not in title.lower():
                continue
            process_img(path, image)
            time.sleep(random.uniform(0.2, 2))
        driver.close()


if __name__ == '__main__':
    print("Working on Main script...")
    main()
    print("Main script successfully executed!")
