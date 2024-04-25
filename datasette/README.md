# Datasette-related instructions

You should execute `run.py` from the root of repository, but it's possible to also execute scripts individually.

### CLI commands

regular order of execution with `run.py` is: `fetch_targets.py` > `load_targets.py` > `build_targets.py`

however, you can:

run `fetch_targets.py` inside of the directory to fetch data and initialize or update database with immunefi bounties. this function invokes `load_targets.py`.

run `load_targets.py` to insert or update database with immunefi bounties from `/projects` directory.

run `datasette serve immunefi_data.db -m metadata.json` afterwards to access datasette UI (`run.py` does that for you)

you can run datasette with additional settings (default for `run.py`)

`datasette serve immunefi_data.db -m metadata.json --setting max_returned_rows 2000`

`metadata.json` contains saved query data, feel free to add more queries like so - https://docs.datasette.io/en/stable/sql_queries.html#canned-queries 