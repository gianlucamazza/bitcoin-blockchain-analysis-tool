import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import logging
from typing import Any, Dict, List
import networkx as nx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def visualize_cluster(cluster_report: Dict[str, Any]) -> None:
    """
    Visualize the cluster of Bitcoin addresses.

    Args:
        cluster_report (Dict[str, Any]): The report containing the cluster information.
    """
    G = nx.Graph()

    # Add nodes and edges based on the cluster information
        # Add nodes and edges based on the cluster information
    for address_info in cluster_report.get("addresses", []):
        address = address_info.get("address")
        if address:
            G.add_node(address)
            transactions_flow = address_info.get("transactions_flow", [])
            for flow in transactions_flow:
                for tx in flow:
                    if isinstance(tx, dict):
                        txid = tx.get("txid")
                        if txid:
                            G.add_node(txid)
                            G.add_edge(address, txid)
                            for output in tx.get("outputs", []):
                                output_address = output.get("address")
                                if output_address:
                                    G.add_node(output_address)
                                    G.add_edge(txid, output_address)

    # Draw the graph
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, k=0.3)
    nx.draw(G, pos, with_labels=True, node_size=500, node_color="skyblue", font_size=8, font_weight="bold", edge_color="gray")
    plt.title("Bitcoin Address Cluster")
    plt.show()


def plot_balance_over_time(address_info: Dict[str, Any]) -> None:
    """
    Plot the balance of a Bitcoin address over time.

    Args:
        address_info (Dict[str, Any]): The address information containing transaction history.
    """
    if "address" not in address_info:
        logger.error("Address information is missing 'address' key")
        return

    transactions = address_info.get("transactions_flow", [])
    balance = 0
    balance_history = []
    timestamps = []

    for tx in transactions:
        tx_time = tx.get('time', 0)
        for output in tx.get("outputs", []):
            if output.get("address") == address_info["address"]:
                balance += output.get("value", 0)
        for input_tx in tx.get("inputs", []):
            if input_tx.get("prevout", {}).get("scriptpubkey_address") == address_info["address"]:
                balance -= input_tx.get("prevout", {}).get("value", 0)

        balance_history.append(balance)
        timestamps.append(pd.to_datetime(tx_time, unit='s'))

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, balance_history, label='Balance over time')
    plt.xlabel('Time')
    plt.ylabel('Balance (BTC)')
    plt.title(f"Balance over time for {address_info['address']}")
    plt.legend()
    plt.show()


def plot_transaction_values(transactions: List[Dict[str, Any]]) -> None:
    """
    Plot a histogram of transaction values.

    Args:
        transactions (List[Dict[str, Any]]): List of transactions.
    """
    values = []
    for tx in transactions:
        for output in tx.get("outputs", []):
            values.append(output.get("value", 0))

    plt.figure(figsize=(10, 5))
    plt.hist(values, bins=50, log=True)
    plt.xlabel('Transaction Value (BTC)')
    plt.ylabel('Frequency')
    plt.title('Histogram of Transaction Values')
    plt.show()


def plot_degree_distribution(G: nx.Graph) -> None:
    """
    Plot the degree distribution of the graph.

    Args:
        G (nx.Graph): The graph to plot the degree distribution for.
    """
    degrees = [G.degree(n) for n in G.nodes()]
    plt.figure(figsize=(10, 5))
    plt.hist(degrees, bins=50, log=True)
    plt.xlabel('Degree')
    plt.ylabel('Frequency')
    plt.title('Degree Distribution')
    plt.show()
