# datasettte serve test_data.db
import json
import sqlite3
import os
import build_targets

# Define the directory containing your JSON files
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
json_directory = os.path.join(parent_directory, "targets", "project")


def connect_db():
    """Connects to the SQLite database and creates tables if they don't exist."""
    conn = sqlite3.connect("immunefi_data.db")
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS bounties (
        bountyId TEXT PRIMARY KEY,
        slug TEXT,
        project TEXT,
        maxBounty INTEGER,
        launchDate TEXT,
        endDate TEXT,
        updatedDate TEXT,
        kyc BOOLEAN,
        programOverview TEXT,
        prioritizedVulnerabilities TEXT,
        rewardsBody TEXT,
        outOfScopeAndRules TEXT,
        assetsBodyV2 TEXT
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS rewards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bountyId TEXT,
        assetType TEXT,
        level TEXT,
        payout TEXT,
        pocRequired BOOLEAN,
        FOREIGN KEY (bountyId) REFERENCES bounties(bountyId)
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bountyId TEXT,
        type TEXT,
        url TEXT,
        description TEXT,
        isPrimacyOfImpact BOOLEAN,
        FOREIGN KEY (bountyId) REFERENCES bounties(bountyId)
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS impacts (
        impactId INTEGER PRIMARY KEY AUTOINCREMENT,
        bountyId TEXT,
        title TEXT,
        type TEXT,
        severity TEXT,
        FOREIGN KEY (bountyId) REFERENCES bounties(bountyId)
    )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bountyId TEXT,
            network TEXT,
            target TEXT,
            updatedDate TEXT,
            FOREIGN KEY (bountyId) REFERENCES bounties(bountyId)
        )
        """
    )

    return conn, cursor


def insert_or_update_data(cursor, bounty):
    cursor.execute(
        "SELECT updatedDate FROM bounties WHERE bountyId = ?", (bounty["id"],)
    )
    result = cursor.fetchone()

    if result:
        if result[0] < bounty["updatedDate"]:
            print("Updating:", bounty["id"])
            cursor.execute(
                """
                UPDATE bounties
                SET slug=?, project=?, maxBounty=?, launchDate=?, endDate=?, updatedDate=?, kyc=?, programOverview=?, prioritizedVulnerabilities=?, rewardsBody=?, outOfScopeAndRules=?, assetsBodyV2=?
                WHERE bountyId=?
            """,
                (
                    bounty["slug"],
                    bounty["project"],
                    bounty["maxBounty"],
                    bounty["launchDate"],
                    bounty["endDate"],
                    bounty["updatedDate"],
                    bounty["kyc"],
                    bounty["id"],
                    # ADDED
                    bounty["programOverview"],
                    bounty["prioritizedVulnerabilities"],
                    bounty["rewardsBody"],
                    bounty["outOfScopeAndRules"],
                    bounty["assetsBodyV2"],
                ),
            )
            update_nested_data(cursor, bounty["id"], bounty)
    else:
        print("Inserting:", bounty["id"])
        cursor.execute(
            """
            INSERT INTO bounties (bountyId, slug, project, maxBounty, launchDate, endDate, updatedDate, kyc, programOverview, prioritizedVulnerabilities, rewardsBody, outOfScopeAndRules, assetsBodyV2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                bounty["id"],
                bounty["slug"],
                bounty["project"],
                bounty["maxBounty"],
                bounty["launchDate"],
                bounty["endDate"],
                bounty["updatedDate"],
                bounty["kyc"],
                # ADDED
                bounty["programOverview"],
                bounty["prioritizedVulnerabilities"],
                bounty["rewardsBody"],
                bounty["outOfScopeAndRules"],
                bounty["assetsBodyV2"],
            ),
        )
        insert_nested_data(cursor, bounty["id"], bounty)


def insert_nested_data(cursor, bounty_id, bounty):
    if "rewards" in bounty:
        for item in bounty["rewards"]:
            cursor.execute(
                """
                INSERT INTO rewards (bountyId, assetType, level, payout, pocRequired)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    bounty_id,
                    item.get("assetType"),
                    item.get("level"),
                    item.get("payout"),
                    item.get("pocRequired"),
                ),
            )
    if "assets" in bounty:
        for item in bounty["assets"]:
            cursor.execute(
                """
                INSERT INTO assets (bountyId, type, url, description, isPrimacyOfImpact)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    bounty_id,
                    item.get("type"),
                    item.get("url"),
                    item.get("description"),
                    item.get("isPrimacyOfImpact"),
                ),
            )
            build_targets.build_targets_row(
                cursor, bounty_id, item.get("url"), bounty["updatedDate"]
            )
    if "impacts" in bounty:
        for item in bounty["impacts"]:
            cursor.execute(
                """
                INSERT INTO impacts (bountyId, title, type, severity)
                VALUES (?, ?, ?, ?)
            """,
                (
                    bounty_id,
                    item.get("title"),
                    item.get("type"),
                    item.get("severity"),
                ),
            )


def update_nested_data(cursor, bounty_id, bounty):
    cursor.execute("DELETE FROM rewards WHERE bountyId = ?", (bounty_id,))
    cursor.execute("DELETE FROM assets WHERE bountyId = ?", (bounty_id,))
    cursor.execute("DELETE FROM impacts WHERE bountyId = ?", (bounty_id,))
    insert_nested_data(cursor, bounty_id, bounty)
 
        
def process_json_files(cursor, json_directory):
    for filename in os.listdir(json_directory):
        if filename.endswith(".json"):
            with open(os.path.join(json_directory, filename), "r") as file:
                data = json.load(file)
                bounty = data["pageProps"]["bounty"]
                insert_or_update_data(cursor, bounty)


def main():
    conn, cursor = connect_db()
    try:
        process_json_files(cursor, json_directory)

        cursor.execute(
            """
            SELECT name FROM sqlite_master WHERE type='view' AND name='quick_view';
            """
        )
        
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE VIEW quick_view AS SELECT bountyId, programOverview, assetsBodyV2 FROM bounties;
                """
            )
            
    finally:
        conn.commit()
        conn.close()


if __name__ == "__main__":
    main()
