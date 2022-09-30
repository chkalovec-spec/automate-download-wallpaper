import random
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
from pathlib import Path
import shutil

BASE_URL = "https://wallpaperscraft.com"
PAGE_URL = "/page"
DOWNLOAD_IMAGE_PAGE_COUNT = 2
CATEGORY_LINK_CLASS = "filter__link"
CATEGORY_LINK_HREF = re.compile("catalog")
IMAGES_LINK_CLASS = "wallpapers__link"
IMAGE_LINK_CLASS = "wallpaper__image"
IMAGE_NAME_CLASS = "wallpaper__tags"
IMAGES_DIR = "Pictures"
WALLPAPERS_DIR = "wallpapers"
WALLPAPER_EXT = "jpg"


def get_soup(url=""):
    r = requests.get(BASE_URL + url)
    return BeautifulSoup(r.text, "lxml")


def get_destination_dir():
    return Path.joinpath(Path.home(), IMAGES_DIR, WALLPAPERS_DIR)


def create_destination_dir():
    dir = get_destination_dir()
    if Path.exists(dir):
        shutil.rmtree(dir)
    Path.mkdir(dir)
    return str(dir)


def get_random_category(categories):
    return random.choice(categories)


def get_categories(soup):
    categories = []
    category_elements = soup.find_all(
        "a", class_=CATEGORY_LINK_CLASS, href=CATEGORY_LINK_HREF
    )
    for data in category_elements:
        category_with_count = data.get_text("|", strip=True)
        category = category_with_count.split("|")[0]
        categories.append(
            {
                "name": category,
                "link": data["href"],
            }
        )
    return categories


def get_image_links(page_link):
    links = []
    for page_num in range(1, DOWNLOAD_IMAGE_PAGE_COUNT + 1):
        images_page_soup = get_soup(f"{page_link}{PAGE_URL}{str(page_num)}")
        images = images_page_soup.find_all("a", class_=IMAGES_LINK_CLASS)
        for data in images:
            links.append(data["href"])
    return links


def download_image(page_link):
    image_page_soup = get_soup(page_link)
    image_element = image_page_soup.find("img", class_=IMAGE_LINK_CLASS)
    image_name_element = image_page_soup.find("div", class_=IMAGE_NAME_CLASS)
    image_name = image_name_element.get_text(strip=True).replace(",", "_")
    image = Image.open(requests.get(image_element["src"], stream=True).raw)
    destination_dir = get_destination_dir()
    image.save(f"{destination_dir}/{image_name}.{ WALLPAPER_EXT}")


def main():
    print("Getting image category...")
    main_page_soup = get_soup()
    categories = get_categories(main_page_soup)
    category = get_random_category(categories)
    print(f"image category selected: {category['name']}")
    image_links = get_image_links(category["link"])

    image_download_left = len(image_links)

    print(f"Links to images successfully received. Total: {image_download_left}")
    create_destination_dir()
    for image_link in image_links:
        image_download_left -= 1
        try:
            print("Downloading the picture...")
            download_image(image_link)
            print(f"Image uploaded successfully!. Left {image_download_left}")
            if image_download_left == 0:
                print("All pictures downloaded!")
        except:
            print(
                f"Image uploaded image uploaded unsuccessfully. Left {image_download_left}"
            )


if __name__ == "__main__":
    main()
