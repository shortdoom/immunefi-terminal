import json
import os
import re
import sqlite3


SUPPORTED_NETWORK = {
    "mainet:": "etherscan.io",
    "optim:": "optimistic.etherscan.io",
    "goerli:": "goerli.etherscan.io",
    "sepolia:": "sepolia.etherscan.io",
    "tobalaba:": "tobalaba.etherscan.io",
    "bsc:": "bscscan.com",
    "testnet.bsc:": "testnet.bscscan.com",
    "arbi:": "arbiscan.io",
    "testnet.arbi:": "testnet.arbiscan.io",
    "poly:": "polygonscan.com",
    "mumbai:": "testnet.polygonscan.com",
    "avax:": "snowtrace.io",
    "testnet.avax:": "testnet.snowtrace.io",
    "ftm:": "ftmscan.com",
    "goerli.base:": "goerli.basescan.org",
    "base:": "basescan.org",
    "gno:": "gnosisscan.io",
    "polyzk:": "zkevm.polygonscan.com",
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
    # Regular expression for matching an Ethereum address
    eth_address_pattern = r"0x[a-fA-F0-9]{40}"

    # Find all occurrences of Ethereum addresses in the URL
    addresses = re.findall(eth_address_pattern, url)

    if addresses:
        # Assuming the first match is the relevant address
        address = addresses[0]
        for network_prefix, domain in SUPPORTED_NETWORK.items():
            if domain in url:
                return f"{network_prefix}{address}"
        # If no matching domain was found, return 'unknown' with the address
        return f"unknown:{address}"
    else:
        # If no address was found, return a placeholder indicating this
        return f"unknown:{url}"


def insert_into_targets(cursor, bounty_id, network_address, updatedDate):
    cursor.execute(
        """
        INSERT INTO targets (bountyId, target, updatedDate)
        VALUES (?, ?, ?)
        """,
        (bounty_id, network_address, updatedDate),
    )


def build_targets_row(cursor, bountyId, url, updatedDate):
    path = extract_network_and_address(url)
    insert_into_targets(cursor, bountyId, path, updatedDate)


def build_targets_table(cursor):
    cursor.execute(
        "SELECT a.id, a.bountyId, a.type, a.url, a.description, a.isPrimacyOfImpact, b.updatedDate FROM assets a JOIN bounties b ON a.bountyId = b.bountyId WHERE a.type = 'smart_contract' AND a.url NOT LIKE '%github%';"
    )
    rows = cursor.fetchall()

    for _, bounty_id, _, url, _, _, updatedDate in rows:
        path = extract_network_and_address(url)
        insert_into_targets(cursor, bounty_id, path, updatedDate)


def main():
    conn, cursor = connect_db()
    try:
        build_targets_table(cursor)
    finally:
        conn.commit()
        conn.close()


if __name__ == "__main__":
    main()
