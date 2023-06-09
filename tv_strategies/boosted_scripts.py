"""
    The script fetches and prints the titles and likes of all popular trading strategies from the TradingView website.
    The data is sorted by the number of likes before being printed.
    This will help you find the best strategies that you can recreate to be optimized in python.
    Please wait a few minutes for script to scrape all webpages.
"""
import requests
from bs4 import BeautifulSoup
import time

def fetch_strategies(page_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    response = requests.get(page_url, headers=headers)

    # If the GET request is successful, the status code will be 200
    if response.status_code != 200:
        return [], None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the strategy blocks
    strategy_blocks = soup.find_all('div', class_='tv-widget-idea js-userlink-popup-anchor')

    strategies = []
    for strategy_block in strategy_blocks:
        # Find the title and likes within each strategy block
        title = strategy_block.find('a',
                                    class_='tv-widget-idea__title apply-overflow-tooltip js-widget-idea__popup').text
        likes = strategy_block.find('span',
                                    class_='tv-card-social-item apply-common-tooltip tv-card-social-item--agrees tv-card-social-item--button tv-card-social-item--border tv-social-row__item').find(
            'span', class_='tv-card-social-item__count').text

        # Convert likes from string to integer
        likes = int(likes)

        # Add the strategy to the list
        strategies.append({"title": title, "likes": likes})

    # Find the link to the next page, if it exists
    next_page_link = soup.find('a', class_='tv-feed-rounded-button tv-feed-pagination__next js-page-reference')

    next_page_url = next_page_link.get('href') if next_page_link else None

    return strategies, next_page_url


def scrape_all_strategies(base_url, start_page):
    all_strategies = []
    next_page_url = base_url + start_page

    while next_page_url:
        strategies, next_page = fetch_strategies(next_page_url)
        all_strategies.extend(strategies)

        # If next page is not None, concatenate it with the base url
        if next_page:
            next_page_url = base_url + next_page
        else:
            next_page_url = None

        # Respectful crawling by sleeping between requests
        time.sleep(1)

    return all_strategies

base_url = 'https://www.tradingview.com'
start_page = '/scripts/?script_type=strategies'

all_strategies = scrape_all_strategies(base_url, start_page)

# Sort the data in descending order by likes.
sorted_strategies = sorted(all_strategies, key=lambda x: x['likes'], reverse=True)

# Print out the sorted data.
for strategy in sorted_strategies:
    print(f'Title: {strategy["title"]}, Likes: {strategy["likes"]}')
