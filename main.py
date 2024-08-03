"""
Bitcoin Blockchain Analysis Tool

This script provides a command-line interface (CLI) for analyzing Bitcoin addresses, transactions, and blocks.
It leverages the `AddressAnalyzer` and `APIClient` classes to interact with the blockchain and generate detailed analysis reports.

Modules:
    - argparse: For parsing command-line arguments.
    - json: For handling JSON data.
    - logging: For logging information.
    - typing: For type hinting.
    - analyzer: Custom module for address analysis.
    - api_client: Custom module for API interactions.

Functions:
    - parse_arguments: Parses command-line arguments.
    - analyze_addresses: Analyzes Bitcoin addresses for wallet clustering and transaction flows.
    - trace_transactions: Traces the flow of transactions for a given address.
    - trace_transaction: Recursively traces a single transaction.
    - analyze_block: Analyzes a block for large transactions.
    - main: Entry point of the script.

Usage:
    python script_name.py --addresses <addresses> --transaction <txid> --block <block_hash> --output <output_file>
"""

import argparse
import json
import logging
from typing import List, Dict, Any

from analyzer import AddressAnalyzer
from api_client import APIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Bitcoin Blockchain Analysis Tool")
    parser.add_argument("--addresses", nargs='+', help="Bitcoin address(es) to analyze")
    parser.add_argument("--transaction", help="Transaction ID to analyze")
    parser.add_argument("--block", help="Block hash to analyze")
    parser.add_argument("--flow-depth", type=int, default=5, help="Depth for transaction flow analysis")
    parser.add_argument("--cluster-depth", type=int, default=2, help="Depth for wallet cluster analysis")
    parser.add_argument("--large-tx-threshold", type=float, default=10, help="Threshold for large transaction detection (in BTC)")
    parser.add_argument("--output", help="Output file for the report (JSON format)")
    return parser.parse_args()

def analyze_addresses(analyzer: AddressAnalyzer, addresses: List[str], flow_depth: int, cluster_depth: int) -> Dict[str, Any]:
    """
    Analyze Bitcoin addresses for wallet clustering and transaction flows.

    Args:
        analyzer (AddressAnalyzer): Instance of AddressAnalyzer.
        addresses (List[str]): List of Bitcoin addresses to analyze.
        flow_depth (int): Depth for transaction flow analysis.
        cluster_depth (int): Depth for wallet cluster analysis.

    Returns:
        Dict[str, Any]: Analysis report for the addresses.
    """
    logger.info(f"Analyzing addresses: {addresses}")
    clusters = analyzer.analyze_wallet_cluster(addresses, depth=cluster_depth)
    return {
        "addresses": addresses,
        "clusters": clusters,
        "transactions_flow": [
            {address: trace_transactions(analyzer, address, flow_depth)}
            for address in addresses
        ]
    }

def trace_transactions(analyzer: AddressAnalyzer, address: str, depth: int) -> List[Dict[str, Any]]:
    """
    Trace transactions for a given address.

    Args:
        analyzer (AddressAnalyzer): Instance of AddressAnalyzer.
        address (str): Bitcoin address to trace transactions for.
        depth (int): Depth for transaction flow analysis.

    Returns:
        List[Dict[str, Any]]: List of traced transactions.
    """
    return [trace_transaction(analyzer, tx['txid'], depth) for tx in analyzer.get_transactions(address)]

def trace_transaction(analyzer: AddressAnalyzer, txid: str, depth: int, current_depth: int = 0) -> Dict[str, Any]:
    """
    Recursively trace a single transaction.

    Args:
        analyzer (AddressAnalyzer): Instance of AddressAnalyzer.
        txid (str): Transaction ID to trace.
        depth (int): Depth for transaction flow analysis.
        current_depth (int): Current recursion depth.

    Returns:
        Dict[str, Any]: Traced transaction information.
    """
    if current_depth >= depth:
        return {"txid": txid, "status": "max depth reached"}
    
    try:
        tx_info = analyzer.api_client.get_transaction_info(txid)
        if not tx_info:
            return {"txid": txid, "status": "transaction not found"}
    except Exception as e:
        logger.error(f"Error fetching transaction info for {txid}: {e}")
        return {"txid": txid, "status": "error fetching transaction info"}
    
    outputs = []
    for vout in tx_info.get('vout', []):
        try:
            spending_tx = analyzer.api_client.get_spending_tx(txid, vout.get('n', 0))
            if spending_tx and spending_tx['spent']:
                outputs.append(trace_transaction(analyzer, spending_tx['txid'], depth, current_depth + 1))
            else:
                outputs.append({
                    "address": vout.get('scriptpubkey_address', 'Unknown'),
                    "value": vout.get('value', 0) / 1e8,
                    "status": "unspent"
                })
        except Exception as e:
            logger.error(f"Error processing output for {txid}: {e}")
            outputs.append({
                "address": vout.get('scriptpubkey_address', 'Unknown'),
                "value": vout.get('value', 0) / 1e8,
                "status": "error processing output"
            })
    
    return {"txid": txid, "inputs": tx_info.get('vin', []), "outputs": outputs}

def analyze_block(analyzer: AddressAnalyzer, block_hash: str, large_tx_threshold: float) -> Dict[str, Any]:
    """
    Analyze a block for large transactions.

    Args:
        analyzer (AddressAnalyzer): Instance of AddressAnalyzer.
        block_hash (str): Block hash to analyze.
        large_tx_threshold (float): Threshold for large transaction detection (in BTC).

    Returns:
        Dict[str, Any]: Analysis report for the block.
    """
    logger.info(f"Analyzing block: {block_hash}")
    try:
        block_info = analyzer.api_client.get_block_info(block_hash)
        large_txs = [tx for tx in block_info.get('tx', []) if tx.get('value', 0) / 1e8 > large_tx_threshold]
        return {"block_info": block_info, "large_transactions": large_txs}
    except Exception as e:
        logger.error(f"Error fetching block info for {block_hash}: {e}")
        return {"block_info": "Error fetching block info", "large_transactions": []}

def main():
    """
    Main entry point for the script.
    Parses arguments and performs analysis based on the provided options.
    """
    args = parse_arguments()
    analyzer = AddressAnalyzer(APIClient())
    report = {"addresses": [], "transaction": None, "block": None}

    if args.addresses:
        addresses_report = analyze_addresses(analyzer, args.addresses, args.flow_depth, args.cluster_depth)
        report["addresses"].append(addresses_report)
        print(json.dumps(addresses_report, indent=2))

    if args.transaction:
        logger.info(f"Analyzing transaction: {args.transaction}")
        transaction_report = trace_transaction(analyzer, args.transaction, args.flow_depth)
        report["transaction"] = transaction_report
        print(json.dumps(transaction_report, indent=2))

    if args.block:
        logger.info(f"Analyzing block: {args.block}")
        block_report = analyze_block(analyzer, args.block, args.large_tx_threshold)
        report["block"] = block_report
        print(json.dumps(block_report, indent=2))

    if not (args.addresses or args.transaction or args.block):
        logger.warning("Please specify addresses, a transaction, or a block to analyze")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Full report saved to {args.output}")

if __name__ == "__main__":
    main()
