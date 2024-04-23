import sqlite3
import argparse
import csv

LOCAL_DB_PATH = "immunefi_data.db"
DEFAULT_CSV_PATH = "to_remove.csv"

'''
Run: python remove_targets.py --target <network>:<address> [--table <table_name>]
If no --target is specified, read from to_remove.csv
If --table is specified, removes the entire specified table instead of individual targets
Remove selected rows or entire tables from targets_data db (useful to clean after working)
'''

def connect_db():
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    return conn, cursor

def remove_targets(targets):
    conn, cursor = connect_db()
    try:
        for target in targets:
            cursor.execute("DELETE FROM targets_data WHERE target = ?", (target,))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def remove_table(table_name):
    conn, cursor = connect_db()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        print(f"Table {table_name} has been removed.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def read_targets_from_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        targets = [row[0] for row in reader]
    return targets

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--target", type=str, help="A single target to remove")
    parser.add_argument("--table", type=str, help="Name of the table to remove entirely")
    args = parser.parse_args()

    if args.table:
        remove_table(args.table)
    elif args.target:
        targets = [args.target]
        remove_targets(targets)
    else:
        targets = read_targets_from_csv(DEFAULT_CSV_PATH)
        remove_targets(targets)
