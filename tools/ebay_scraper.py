from bs4 import BeautifulSoup
from PIL import Image
import requests
import json
import os
import io


def scrape_images(search_string, destination_folder):
    search_string = search_string.replace(' ', '+')
    soup = soup_from_url(
        f'https://www.ebay.com/sch/i.html?_nkw={search_string}&_ipg=200')
    items = soup.select('.s-item__link')

    count = 0
    for item in items:
        count += 1
        print_progress_bar(search_string, count, len(items))

        item_soup = soup_from_url(item['href'])
        for image_url in get_image_urls(item_soup):
            download_image(image_url, destination_folder)
    print()


def get_image_urls(item_soup):
    image_urls = set()
    for thumbnail in item_soup.select('.tdThumb'):
        image_url = thumbnail.find('img')['src']
        image_url = image_url.replace('/s-l64', '/s-l1600')
        image_urls.add(image_url)
    return image_urls


def download_image(image_url, destination_folder):
    file_name = image_url.split('/')[-2]
    if not os.path.isfile(f'ebay_images/{destination_folder}/{file_name}.jpg'):
        image = requests.get(image_url)
        if image.status_code == 200:
            mkdir(f'ebay_images/{destination_folder}')
            image = Image.open(io.BytesIO(image._content))
            image = crop_and_resize(image)
            image.save(
                f'ebay_images/{destination_folder}/{file_name}.jpg')


def crop_and_resize(image):
    width = image.size[0]
    height = image.size[1]
    dim = min(width, height)

    top = (height - dim) // 2
    left = (width - dim) // 2
    bottom = top + dim
    right = left + dim

    image = image.crop((left, top, right, bottom))
    image = image.resize((224, 224))
    image = image.convert('RGB')
    return image


def soup_from_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def print_progress_bar(search_string, count, total, size=32):
    progress = (count / total) * 100
    progress_bar = '['
    draw_arrow = True
    for i in range(size):
        if (i + 1) * (100 / size) <= progress:
            progress_bar += '='
        elif draw_arrow == True and progress != 100:
            progress_bar += '>'
            draw_arrow = False
        else:
            if draw_arrow == True:
                progress_bar += '>'
                draw_arrow = False
            else:
                progress_bar += ' '
    bar = f'({search_string}) {progress_bar}] {count}/{total} {progress:.2f}%'
    print(bar, end='\r')


def mkdir(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)


def main():
    mkdir('ebay_images/')
    searches = json.load(open('tools/json/ebay_searches.json'))
    for search in searches:
        scrape_images(search['search_string'], search['destination_folder'])


if __name__ == '__main__':
    main()
