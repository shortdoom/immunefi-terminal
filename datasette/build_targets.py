import re
import sqlite3

SUPPORTED_NETWORK = {
    "mainet": "etherscan.io",
    "optim": "optimistic.etherscan.io",
    "goerli": "goerli.etherscan.io",
    "sepolia": "sepolia.etherscan.io",
    "tobalaba": "tobalaba.etherscan.io",
    "bsc": "bscscan.com",
    "testnet.bsc": "testnet.bscscan.com",
    "arbi": "arbiscan.io",
    "testnet.arbi": "testnet.arbiscan.io",
    "poly": "polygonscan.com",
    "mumbai": "testnet.polygonscan.com",
    "avax": "snowtrace.io",
    "testnet.avax": "testnet.snowtrace.io",
    "ftm": "ftmscan.com",
    "goerli.base": "goerli.basescan.org",
    "base": "basescan.org",
    "gno": "gnosisscan.io",
    "polyzk": "zkevm.polygonscan.com",
}

PATH_TO_DB = "immunefi_data.db"


def connect_db():
    conn = sqlite3.connect(PATH_TO_DB)
    cursor = conn.cursor()
    return conn, cursor


def extract_network_and_address(url):
    """
    Extracts the network name and smart contract address from the given URL using regular expression.
    Builds slither target argument <network>:<path>
    """
    eth_address_pattern = r"0x[a-fA-F0-9]{40}"

    addresses = re.findall(eth_address_pattern, url)

    if addresses:
        address = addresses[0]
        for network_prefix, domain in SUPPORTED_NETWORK.items():
            if domain in url:
                return network_prefix, f"{network_prefix}:{address}"
        return "unknown", address
    else:
        return "unknown", url


def insert_into_targets(cursor, bounty_id, network, path, updatedDate):
    cursor.execute(
        """
        INSERT INTO targets (bountyId, network, target, updatedDate)
        VALUES (?, ?, ?, ?)
        """,
        (bounty_id, network, path, updatedDate),
    )


def build_targets_row(cursor, bountyId, url, updatedDate):
    network, path = extract_network_and_address(url)
    insert_into_targets(cursor, bountyId, network, path, updatedDate)
