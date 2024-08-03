import requests
import json
import time
import logging
from requests.exceptions import RequestException
import diskcache as dc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, max_retries=3, retry_delay=3, cache_dir='cache'):
        self.base_url = "https://blockstream.info/api"
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cache = dc.Cache(cache_dir)

    def _make_request(self, url):
        # Check cache first
        if url in self.cache:
            logger.info(f"Returning cached response for URL: {url}")
            return self.cache[url]

        logger.info(f"Making request to URL: {url}")
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for bad status codes
                logger.info(f"Received response from {url}: {response.status_code}")
                data = response.json()
                self.cache[url] = data  # Store response in cache
                return data
            except RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed. Error making request to {url}: {e}")
                if attempt + 1 < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Max retries reached. Giving up.")
                    return None
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from {url}: {e}")
                logger.error(f"Response content: {response.text}")
                return None

    def get_address_info(self, address):
        url = f"{self.base_url}/address/{address}"
        logger.info(f"Fetching address info for: {address}")
        return self._make_request(url)

    def get_transactions(self, address):
        url = f"{self.base_url}/address/{address}/txs"
        logger.info(f"Fetching transactions for address: {address}")
        return self._make_request(url)

    def get_transaction_info(self, txid):
        url = f"{self.base_url}/tx/{txid}"
        logger.info(f"Fetching transaction info for TXID: {txid}")
        return self._make_request(url)

    def get_spending_tx(self, txid, vout):
        url = f"{self.base_url}/tx/{txid}/outspend/{vout}"
        logger.info(f"Fetching spending transaction for TXID: {txid}, VOUT: {vout}")
        return self._make_request(url)

    def get_block_info(self, block_hash):
        url = f"{self.base_url}/block/{block_hash}"
        logger.info(f"Fetching block info for block hash: {block_hash}")
        return self._make_request(url)

    def get_bitcoin_price(self, date):
        url = f"{self.coingecko_url}/coins/bitcoin/history?date={date}"
        logger.info(f"Fetching Bitcoin price for date: {date}")
        data = self._make_request(url)
        if data and 'market_data' in data:
            price = data['market_data']['current_price']['usd']
            logger.info(f"Bitcoin price on {date}: {price} USD")
            return price
        logger.warning(f"Market data not found in response for date: {date}")
        return None
