# Importing Necessary Libraries
import random
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import logging
import asyncio
from aiohttp import ClientSession
import pandas as pd
import time
from typing import Dict, List, Optional, Tuple

# Setting up config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom headers to mimic human interaction with websites
CUSTOM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "DNT": "1"
}

# Feature list across all laptops
DETAIL_LISTING = set()

async def request_with_retries(url: str, headers: Dict[str, str], session: ClientSession, retries: int = 10) -> Optional[str]:
    """
    Request a URL with retries and exponential backoff.

    Args:
        url (str): The URL to request.
        headers (Dict[str, str]): Headers to include in the request.
        session (ClientSession): The aiohttp session.
        retries (int): Number of retry attempts.

    Returns:
        Optional[str]: The innerHTML content if successful, None otherwise.
    """
    for attempt in range(retries):
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                text = await response.text()
                soup = BeautifulSoup(text, "lxml")
                if soup.select_one("title").get_text() == "Robot Check":
                    logging.warning("CAPTCHA page detected... retrying")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return text
            else:
                logging.warning(f"Failed to retrieve the page. Status code: {response.status}... retrying")
                await asyncio.sleep(2 ** attempt)
    return None

async def parse_item_card(item: BeautifulSoup) -> Dict[str, str]:
    """
    Parse an individual item card to extract laptop information.

    Args:
        item (BeautifulSoup): The BeautifulSoup object representing the item card.

    Returns:
        Dict[str, str]: A dictionary containing the laptop information.
    """
    laptop_info: Dict[str, str] = {}

    # Laptop ID
    id_element = item.select_one("div.bx_catalog_item_scu_code")
    if id_element:
        idd = id_element.attrs.get("text")
        laptop_info["laptop id"] = idd

    # Brand and model of laptop
    title_element = item.select_one("div.bx_catalog_item_title")
    if title_element:
        title = " ".join(title_element.select_one("a").attrs.get("title").split()[1:-1])
        laptop_info["title"] = title
    
    # Both old and current price for laptop
    price_element = item.select_one("div.bx_catalog_item_price")
    if price_element:
        old_price_element = price_element.select_one(".old_price")
        curr_price_element = price_element.select_one(".current_price")

        if old_price_element and curr_price_element:
            old_price = old_price_element.get_text(strip=True)
            current_price = curr_price_element.get_text(strip=True)

            laptop_info["old price"] = old_price
            laptop_info["current price"] = current_price

    # All technical information including GPU, CPU, RAM configurations
    specs_element = item.select_one("div.bx_catalog_item_spec")
    if specs_element:
        specs = specs_element.select("div")
        for spec in specs:
            key_element = spec.select_one(".bx_catalog_item_prop")
            value_element = spec.select_one(".bx_catalog_item_value")
            if key_element and value_element:
                key = key_element.get_text(strip=True)[:-1]
                value = value_element.get_text(strip=True)
                laptop_info[key] = value

    # Link on the laptop image (for further purposes)
    image_element = item.select_one('.item_image_container img')
    if image_element and 'data-src' in image_element.attrs:
        image_link = image_element['data-src']
        laptop_info["image link"] = image_link

    return laptop_info

async def parse_listing(url: str, session: ClientSession) -> Tuple[List[Dict[str, str]], Optional[BeautifulSoup]]:

    products: List[Dict[str, str]] = []

    response = await request_with_retries(url, CUSTOM_HEADERS, session)
    if not response:
        return products, None
    
    soup = BeautifulSoup(response, "lxml")
    item_cards = soup.select("[data-id]")

    tasks = []
    for item in item_cards:
        tasks.append(asyncio.ensure_future(parse_item_card(item)))

    results = await asyncio.gather(*tasks)

    for product in results:
        if product:
            for key in product.keys():
                DETAIL_LISTING.add(key)
            products.append(product)
    
    return products, soup

def get_next_page_url(soup: BeautifulSoup) -> Optional[str]:
    """
    Get the URL of the next page from the listing page.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the current page.

    Returns:
        Optional[str]: The URL of the next page, if found. None otherwise.
    """
    # Extract next button on the webpage
    next_button = soup.select_one("li.bx-pag-next a")
    if next_button:
        return urljoin("https://shop.kz", next_button["href"])
    return None

def save_csv(product_list: List[Dict[str, str]], name: str = "laptops.csv") -> None:
    """
    Save the product list to a CSV file.

    Args:
        product_list (List[Dict[str, str]]): The list of product dictionaries.
        name (str): The name of the CSV file.

    Returns:
        None
    """
    df = pd.DataFrame(product_list)
    df.to_csv(name, index=False)

    logging.info(f"Dataset was saved with dirname: {name}")

async def execute_full_scraping(url: str) -> None:
    """
    Execute the full scraping process starting from the given URL.

    Args:
        url (str): The starting URL for scraping.

    Returns:
        None
    """
    current_url = url
    laptops: List[Dict[str, str]] = []

    async with ClientSession() as session:
        max_page_parse = 100 # Number of page needed to parse

        start_time = time.time()
        logging.info(f"Started scraping at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
        
        for page in range(1, max_page_parse + 1):
            logging.info(f"Parsing page {page}")

            listing, soup = await parse_listing(current_url, session)
            laptops.extend(listing)
            next_page_url = get_next_page_url(soup)
            
            print(f"Next page url: {next_page_url}\n")

            if next_page_url:
                current_url = next_page_url
                await asyncio.sleep(random.uniform(2, 6))
            else:
                logging.error("Next page was not found") # Case when next page btn was not found
                break

        save_csv(laptops)

        end_time = time.time()
        logging.info(f"Finished scraping at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
        logging.info(f"Total time taken: {round((end_time - start_time), 2)} seconds")

async def main() -> None:
    await execute_full_scraping("https://shop.kz/offers/noutbuki/")

if __name__ == "__main__":
    asyncio.run(main())
