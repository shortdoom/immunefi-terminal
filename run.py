import os
import argparse
import subprocess


def main():
    subprocess.run(["python", "datasette/fetch_targets.py"])
    os.chdir("datasette")
    subprocess.run(
        [
            "datasette",
            "serve",
            "immunefi_data.db",
            "-m",
            "metadata.json",
            "--setting",
            "max_returned_rows",
            "2000",
        ]
    )

if __name__ == "__main__":
    main()
