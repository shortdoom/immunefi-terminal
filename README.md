# Immunefi-terminal

The only crypto bug bounty terminal you'll ever need.

1. **Use Datasette to browse all available bug bounties on Immunefi.**
2. Construct complex SQL queries with your personal bug bounty data warehouse.
3. Fetch updates from Immunefi for any project.
4. Find repositories and on-chain addresses you want to audit.
5. **Hassle-free download of any source code from any bug bounty program.**
6. Guaranteed compilation of on-chain targets with *patched* crytic-compile.
7. Publish your data with Datasette.

## Installation

Create a new Python environment, e.g., `python3 -m venv venv`.

Install all dependencies with `pip install -r requirements.txt`.

## Running the Dashboard

Execute `python run.py` to initialize the database. This will serve you a dashboard at `127.0.0.1:8001`.

If `immunefi_data.db` is already present, `run.py` will look for new updates to insert.

You can inspect new updates in `updates` table or by checking `git diff` / `git log` inside of the `targets` directory.

## Running the Downloader

`python download.py` takes three arguments:

`python download.py --bountyId <name> --target <network>:<address> --csv /path/to/targets.csv`

`bountyId`: Download all targets for a specific bountyId (from SQLite database).

`target`: Download single `<network>:<address>` target source code (for convenience).

`csv`: Download from a CSV file containing targets (single column with list of `<network>:<address>`).

The script is integrated with `immunefi_data.db` for the bountyId argument. Find your bountyId in the UI and pass it as an argument to `download.py --bountyId <name>`.

All files are saved to the `/files` directory. Slither (if installed) will run out of the box.

## Development

Feel free to experiment with Datasette canned queries, views, and additional table creation. All SQL operations are read from the `sql_data` directory. If something goes terribly wrong, just delete the whole database and start from scratch. Rebuilding takes seconds (you'll lose your `updates` table though).

Good resources to understand Datasette (and SQL) better:

https://datasette.io/tutorials/explore

https://datasette.io/tutorials/learn-sql

## Acknowledgments

This project is possible thanks to:

https://github.com/simonw/datasette

https://github.com/crytic/crytic-compile

https://github.com/infosec-us-team/Immunefi-Bug-Bounty-Programs-Unofficial

## Similar Projects

https://github.com/JoranHonig/bh

https://github.com/tintinweb/bugbounty-companion

## End

Contact on Twitter for paid work. Specializing in blockchain engineering, security, automation. Python, Solidity, JS, and TS focus.