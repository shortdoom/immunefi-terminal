run `fetch_targets.py` inside of the directory to fetch data and initialize or update database with immunefi bounties. invokes `load_targets.py`

run `load_targets.py` to insert or update database with immunefi bounties from `/projects` directory

run `datasette serve immunefi_data.db -m metadata.json` afterwards to access db

or 

`datasette serve immunefi_data.db -m metadata.json --setting max_returned_rows 2000`

`metadata.json` contains saved query data https://docs.datasette.io/en/stable/sql_queries.html#canned-queries

select individual data in datasette dashboard

OR

`targets_run.py --bountyId <name>` -- will load targets from the db and download neccessary data