# Bitcoin Blockchain Analysis Tool

## Overview

The Bitcoin Blockchain Analysis Tool is a command-line interface (CLI) application designed to analyze Bitcoin addresses, transactions, and blocks. It provides detailed insights into wallet clustering, transaction flows, and large transactions within blocks.

## Features

- **Address Analysis**: Analyze Bitcoin addresses for wallet clustering and transaction flows.
- **Transaction Tracing**: Trace the flow of transactions for given addresses up to a specified depth.
- **Block Analysis**: Analyze blocks for large transactions above a specified threshold.
- **Detailed Reports**: Generate and save detailed analysis reports in JSON format.
- **Local Database Cache**: Utilize a local SQLite database to cache API responses, improving performance and reducing redundant API calls.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/gianlucamazza/bitcoin-blockchain-analysis-tool.git
    ```
2. Navigate to the project directory:
    ```bash
    cd bitcoin-blockchain-analysis-tool
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The script can be run from the command line with various options for analysis. Below are some usage examples:

### Command-Line Options

- `--addresses`: Bitcoin address(es) to analyze.
- `--transaction`: Transaction ID to analyze.
- `--block`: Block hash to analyze.
- `--flow-depth`: Depth for transaction flow analysis (default: 5).
- `--cluster-depth`: Depth for wallet cluster analysis (default: 2).
- `--large-tx-threshold`: Threshold for large transaction detection in BTC (default: 10).
- `--output`: Output file for the report in JSON format.

### Examples

#### Analyze Addresses

To analyze one or more Bitcoin addresses:
```bash
python script_name.py --addresses address1 address2 --flow-depth 3 --cluster-depth 2
```

#### Analyze a Transaction

To analyze a specific transaction:
```bash
python script_name.py --transaction txid --flow-depth 3
```

#### Analyze a Block

To analyze a specific block:
```bash
python script_name.py --block block_hash --large-tx-threshold 20
```

#### Save the Report

To save the analysis report to a file:
```bash
python script_name.py --addresses address1 address2 --output report.json
```

## Logging

The tool uses Python's logging module to provide detailed logs of its operations. Logs are printed to the console to help trace the execution and identify any issues.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure your code follows the existing coding style and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.