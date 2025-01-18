import os
import subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))


def main():
    datasette_dir = os.path.join(script_dir, "datasette")
    os.chdir(datasette_dir)
    subprocess.run(["python3", "fetch_targets.py"])
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
