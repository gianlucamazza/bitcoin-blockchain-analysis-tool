import matplotlib.pyplot as plt
import networkx as nx

def visualize_transaction_flow(G, txid, save_path=None):
    """
    Visualize the transaction flow of a given transaction ID using a NetworkX graph.

    Args:
        G (networkx.DiGraph): Directed graph representing the transaction flow.
        txid (str): Transaction ID being visualized.
        save_path (str, optional): Path to save the plot as an image. Defaults to None.

    Returns:
        None
    """
    pos = nx.spring_layout(G, k=0.5)
    plt.figure(figsize=(14, 10))
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=700, edgecolors='black')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20, edge_color='gray')
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_color='black')
    
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'value')
    formatted_edge_labels = {k: f'{v:.2f} BTC' for k, v in edge_labels.items()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=formatted_edge_labels, font_color='red', font_size=8)
    
    plt.title(f"Transaction Flow: {txid}", fontsize=15)
    plt.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"Transaction flow plot saved to {save_path}")
    
    plt.show()

def visualize_address_history(address, total_received, total_sent, current_balance, save_path=None):
    """
    Visualize the history of a Bitcoin address with a pie chart showing total received, total sent, and current balance.

    Args:
        address (str): Bitcoin address being visualized.
        total_received (float): Total BTC received by the address.
        total_sent (float): Total BTC sent from the address.
        current_balance (float): Current BTC balance of the address.
        save_path (str, optional): Path to save the plot as an image. Defaults to None.

    Returns:
        None
    """
    labels = ['Total Received (BTC)', 'Total Sent (BTC)', 'Current Balance (BTC)']
    values = [total_received, total_sent, current_balance]
    colors = ['#ff9999','#66b3ff','#99ff99']
    
    fig, ax = plt.subplots(figsize=(8, 8))
    _, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, textprops=dict(color="w"))
    
    # Enhance the pie chart
    for text in texts:
        text.set_fontsize(12)
    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_color('black')
    
    ax.axis('equal')
    plt.title(f'Bitcoin Address History for {address}', fontsize=15)
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path)
        print(f"Address history plot saved to {save_path}")
    
    plt.show()
