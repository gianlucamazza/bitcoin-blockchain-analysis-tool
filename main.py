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
    - trace_transaction: Recursively traces a single transaction.
    - analyze_block: Analyzes a block for large transactions.
    - main: Entry point of the script.

Usage:
    python script_name.py --addresses <addresses> --transaction <txid> --block <block_hash> --output <output_file>
"""

import json
import logging

from cli import parse_arguments
from analyzer import AddressAnalyzer
from utils import analyze_addresses, trace_transaction, analyze_block
from api_client import APIClient
from visualization import visualize_cluster

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        report["addresses"].extend(addresses_report["addresses"])
        report["clusters"] = addresses_report["clusters"]
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

    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    logger.info(f"Full report saved to {args.output}")

    if args.addresses:
        visualize_cluster(report)
    

if __name__ == "__main__":
    main()
