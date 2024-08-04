import argparse

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
    parser.add_argument("--output", default="report.json", help="Output file for analysis results")
    return parser.parse_args()
