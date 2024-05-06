from collections import deque
from crytic_compile import CryticCompile
import sqlite3
import argparse
import time
import re
import os
import csv
import requests
import shutil
from git import Repo

"""
Download source code for targets from the Immunefi database.

Usage:
    python download.py --bountyId <name> 
                       --target <network>:<address> 
                       --csv /path/to/file.csv

Args:
    bountyId: Download all targets for a specific bountyId (from sqlite database)
    target: Download single <network>:<address> target source code (for convenience)
    csv: Download from a CSV file containing targets (single column of <network>:<address>)

"""

script_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(script_dir)

# NOTE: external integration
if os.path.exists(os.path.join(parent_dir, "core")):
    output_dir = os.path.join(parent_dir, "core", "files", "out")
else:
    output_dir = os.path.join(script_dir, "files")
    
db_path = os.path.join(script_dir, "datasette/immunefi_data.db")


def connect_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return conn, cursor


def get_targets(bountyId):
    conn, cursor = connect_db()
    cursor.execute(
        "SELECT target FROM targets WHERE bountyId = ?",
        (bountyId,),
    )
    targets = [item[0] for item in cursor.fetchall()]
    conn.close()
    return targets


def get_targets_from_csv(csv_file_path):
    with open(csv_file_path, "r") as file:
        reader = csv.reader(file)
        targets = [row[0] for row in reader]
    return targets


def sort_targets(targets):
    repo_targets = []
    file_targets = []
    network_targets = []
    error_targets = []

    for target in targets:
        # Check if target is a GitHub repository
        if re.match(r"^https://github\.com/[^/]+/[^/]+/?$", target):
            repo_targets.append(target)
        # Check if target is a GitHub file
        elif re.match(r"^https://github\.com/[^/]+/[^/]+/blob/.*$", target):
            file_targets.append(target)
        # Check if target is of the form network:address
        elif ":" in target and not "/" in target:
            network_targets.append(target)
        else:
            error_targets.append(target)

    return repo_targets, file_targets, network_targets, error_targets


def clean_crytic_directory(target):
    crytic_path = os.path.join(output_dir, "etherscan-contracts")

    for contract_item in os.listdir(crytic_path):
        contract_item_path = os.path.join(crytic_path, contract_item)

        if contract_item == "crytic_compile.config.json":
            continue

        try:
            _, target_name_from_dir = contract_item.split("-", 1)
            if "-" in target_name_from_dir:
                _, contract_name = target_name_from_dir.rsplit("-", 1)
            else:
                contract_name = target_name_from_dir

            target_output = os.path.join(output_dir, f"{target}:{target_name_from_dir}")
            
            if os.path.exists(target_output):
                shutil.rmtree(crytic_path)
                print(f"Directory {target_output} already exists. Skipping.")
                continue
            
            os.mkdir(target_output)

            if os.path.isfile(contract_item_path):
                shutil.move(
                    contract_item_path,
                    os.path.join(target_output, f"{contract_name}"),
                )

                # Move the crytic_compile.config.json too
                json_file = os.path.join(crytic_path, "crytic_compile.config.json")
                if os.path.exists(json_file):
                    shutil.move(
                        json_file,
                        target_output,
                    )
            else:
                contract_items = os.listdir(contract_item_path)
                for item in contract_items:
                    shutil.move(os.path.join(contract_item_path, item), target_output)

            # Delete the old directory
            shutil.rmtree(contract_item_path)
            shutil.rmtree(crytic_path)

        except Exception as e:
            raise Exception(f"Error processing {contract_item}: {e}")


def download_source(targets):
    repo_targets, file_targets, network_targets, error_targets = sort_targets(targets)

    # deque to hold the timestamps of the last 5 requests
    timestamps = deque(maxlen=5)

    # Enter /files
    os.chdir(output_dir)

    for target in repo_targets:
        try:
            Repo.clone_from(target, os.path.join(output_dir, target.split("/")[-1]))
        except Exception as e:
            raise Exception(f"Error repo_targets: {e}")

    for target in file_targets:
        try:
            raw_url = target.replace(
                "https://github.com", "https://raw.githubusercontent.com"
            )
            raw_url = raw_url.replace("/blob", "")
            r = requests.get(raw_url)
            with open(os.path.join(output_dir, target.split("/")[-1]), "wb") as f:
                f.write(r.content)
        except Exception as e:
            raise Exception(f"Error file_targets: {e}")

    for target in network_targets:
        # Rate limit requests to max 5 requests in 5 secondss
        while len(timestamps) == 5 and time.time() - timestamps[0] < 1:
            time.sleep(1 - (time.time() - timestamps[0]))
        if len(timestamps) == 5:
            timestamps.popleft()
        timestamps.append(time.time())

        try:
            crytic_object = CryticCompile(target, export_dir=output_dir)
            if crytic_object.bytecode_only:
                raise Exception("Error: Bytecode only accessible")
            else:
                clean_crytic_directory(target)
        except Exception as e:
            raise Exception(f"Error network_targets: {e}")

    for target in error_targets:
        print(f"Error error_targets: Invalid target {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run targets against the app and filter the results"
    )
    parser.add_argument(
        "--bountyId", help="Download all targets for a specific bountyId"
    )
    parser.add_argument(
        "--target", help="Download single <network>:<address> target source code"
    )
    parser.add_argument("--csv", help="Download from a CSV file containing targets")
    args = parser.parse_args()

    if args.target:
        targets = [args.target]
    elif args.csv:
        targets = get_targets_from_csv(args.csv)
    else:
        targets = get_targets(args.bountyId)

    download_source(targets)
