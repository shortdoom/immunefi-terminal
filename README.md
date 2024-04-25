# Immunefi-terminal

The only crypto bug bounty terminal you'll ever need.

1. **Use datasette to browse all of the available bug bounties on Immunefi**
2. Construct complex SQL queries with your personal bug bounty data warehouse
3. Fetch updates from Immunefi for any project
4. Find respotiories and on-chain addresses you want to audit
5. **Hassle-free download of any source code from any bug bounty program**
6. Guaranteed compilation of on-chain targets with *patched* crytic-compile
7. Publish your data with datasette

## Install

Create new python enviroment ie. `python3 -m venv venv`

Install all dependencies `pip install requirements.txt`

## Run dashboard

Execute `python run.py` to initialize database. It will serve you a dashboard at `127.0.0.1:8001`

If `immunefi_data.db` is already present, `run.py` will look for new updates to insert. 

Feel free to experiment with datasette canned queries, views and additional table creation. Just delete your .db after you're done - rebuilding takes seconds.

## Run downloader

`download.py` allows for three arguments

`python download.py --bountyId <name> --target <network>:<address> --csv /path/to/targets.csv`

`bountyId`: Download all targets for a specific bountyId (from sqlite database)

`target`: Download single `<network>:<address>` target source code (for convenience)

`csv`: Download from a CSV file containing targets (single column of `<network>:<address>`)

Script is integrated with immunefi_data.db for bountyId argument. Find your bountyId in UI and feed it to `download.py`.

All files are saved to `/files` directory.