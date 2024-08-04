import logging
from typing import List, Set, Dict, Any, Optional
from api_client import APIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AddressAnalyzer:
    """
    Analyzes Bitcoin addresses, including transaction history, balance, and clustering of addresses.
    """
    
    def __init__(self, api_client: APIClient):
        """
        Initialize the AddressAnalyzer with an APIClient.
        
        Parameters:
        - api_client (APIClient): The client used to interact with the Bitcoin API.
        """
        self.api_client = api_client
        self.explored_transactions: Set[str] = set()
        self.explored_addresses: Set[str] = set()
        self.max_depth = 5

    def analyze(self, address: str) -> Optional[int]:
        """
        Analyze the balance and transaction count of a Bitcoin address.
        
        Parameters:
        - address (str): The Bitcoin address to analyze.
        
        Returns:
        - Optional[int]: The balance of the address in satoshis, or None if an error occurred.
        """
        try:
            info = self.api_client.get_address_info(address)
            if info is None:
                logger.error(f"Unable to retrieve information for address: {address}")
                return None

            logger.info(f"Analyzing address: {address}")
            balance = self._calculate_balance(info)
            tx_count = info.get('chain_stats', {}).get('tx_count', 0)

            logger.info(f"Current balance: {balance} satoshi ({balance / 1e8:.8f} BTC)")
            logger.info(f"Total number of transactions: {tx_count}")
            return balance
        except (KeyError, TypeError) as e:
            logger.error(f"Error analyzing address {address}: {e}")
            return None

    def _calculate_balance(self, info: Dict[str, Any]) -> int:
        """
        Calculate the balance of a Bitcoin address from its information.
        
        Parameters:
        - info (Dict[str, Any]): The address information.
        
        Returns:
        - int: The balance of the address in satoshis.
        """
        chain_stats = info.get('chain_stats', {})
        funded_txo_sum = chain_stats.get('funded_txo_sum', 0)
        spent_txo_sum = chain_stats.get('spent_txo_sum', 0)
        return funded_txo_sum - spent_txo_sum

    def get_transactions(self, address: str) -> List[Dict[str, Any]]:
        """
        Retrieve transactions for a Bitcoin address.
        
        Parameters:
        - address (str): The Bitcoin address to get transactions for.
        
        Returns:
        - List[Dict[str, Any]]: A list of transactions, or an empty list if an error occurred.
        """
        try:
            transactions = self.api_client.get_transactions(address)
            if transactions is None:
                logger.error(f"Unable to retrieve transactions for address: {address}")
                return []
            return transactions
        except (KeyError, TypeError) as e:
            logger.error(f"Error retrieving transactions for address {address}: {e}")
            return []

    def analyze_wallet_cluster(self, addresses: List[str], depth: int = 2) -> None:
        """
        Analyze a cluster of Bitcoin addresses to find connected addresses and their balances.
        
        Parameters:
        - addresses (List[str]): A list of Bitcoin addresses to start the analysis from.
        - depth (int): The depth of the cluster exploration (default is 2).
        """
        try:
            depth = min(depth, self.max_depth)
            cluster = set(addresses)
            self.explored_transactions.clear()
            self.explored_addresses.clear()
            for address in addresses:
                self._explore_cluster(address, cluster, depth)
            logger.info("Cluster of addresses connected to the provided addresses:")
            for addr in cluster:
                balance = self.analyze(addr)
                if balance is not None:
                    logger.info(f"Address: {addr}, Balance: {balance / 1e8:.8f} BTC")
        except (KeyError, TypeError) as e:
            logger.error(f"Error analyzing wallet cluster for addresses {addresses}: {e}")

    def _explore_cluster(self, address: str, cluster: Set[str], depth: int) -> None:
        """
        Recursively explore the cluster of addresses connected to a given address.
        
        Parameters:
        - address (str): The Bitcoin address to explore.
        - cluster (Set[str]): The set of addresses that are part of the cluster.
        - depth (int): The remaining depth to explore.
        """
        if depth <= 0 or address in self.explored_addresses:
            return
        self.explored_addresses.add(address)
        cluster.add(address)
        try:
            transactions = self.get_transactions(address)[:100]
            for tx in transactions:
                if tx['txid'] in self.explored_transactions:
                    continue
                self.explored_transactions.add(tx['txid'])

                tx_info = self.api_client.get_transaction_info(tx['txid'])
                if tx_info is None:
                    logger.error(f"Unable to retrieve transaction info for txid: {tx['txid']}")
                    continue

                for vin in tx_info.get('vin', []):
                    prevout_address = vin.get('prevout', {}).get('scriptpubkey_address')
                    if prevout_address and prevout_address not in cluster:
                        self._explore_cluster(prevout_address, cluster, depth - 1)

                for vout in tx_info.get('vout', []):
                    vout_address = vout.get('scriptpubkey_address')
                    if vout_address and vout_address not in cluster:
                        self._explore_cluster(vout_address, cluster, depth - 1)
        except (KeyError, TypeError) as e:
            logger.error(f"Error exploring cluster for address {address}: {e}")
