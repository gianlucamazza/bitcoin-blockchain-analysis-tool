import logging
from typing import Any, Dict, List
from analyzer import AddressAnalyzer

logger = logging.getLogger(__name__)

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
    address_reports = []
    for address in addresses:
        transactions = analyzer.get_transactions(address)
        transactions_flow = [trace_transaction(analyzer, tx['txid'], flow_depth) for tx in transactions]
        address_reports.append({
            "address": address,
            "transactions_flow": transactions_flow
        })
    clusters = analyzer.analyze_wallet_cluster(addresses, depth=cluster_depth)
    return {
        "addresses": address_reports,
        "clusters": clusters
    }

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
    block_info = analyzer.api_client.get_block_info(block_hash)
    large_txs = [tx for tx in block_info.get('tx', []) if tx.get('value', 0) / 1e8 > large_tx_threshold]
    return {"block_info": block_info, "large_transactions": large_txs}
