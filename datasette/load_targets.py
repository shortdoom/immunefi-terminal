import json
import sqlite3
import os
import build_targets
import sql_data.sql_queries
import sql_data.sql_views

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
json_directory = os.path.join(parent_directory, "targets", "project")


def connect_db():
    """Connects to the SQLite database and creates tables if they don't exist."""
    conn = sqlite3.connect("immunefi_data.db")
    cursor = conn.cursor()

    cursor.execute(sql_data.sql_queries.CREATE_TABLE_BOUNTIES)

    cursor.execute(sql_data.sql_queries.CREATE_TABLE_REWARDS)

    cursor.execute(sql_data.sql_queries.CREATE_TABLE_ASSETS)

    cursor.execute(sql_data.sql_queries.CREATE_TABLE_IMPACTS)

    cursor.execute(sql_data.sql_queries.CREATE_TABLE_TAGS)

    cursor.execute(sql_data.sql_queries.CREATE_TABLE_TARGETS)

    cursor.execute(sql_data.sql_queries.CREATE_TABLE_UPDATES)

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
                SET programOverview=?, prioritizedVulnerabilities=?, rewardsBody=?, outOfScopeAndRules=?, assetsBodyV2=?, project=?, maxBounty=?, launchDate=?, endDate=?, updatedDate=?, kyc=?
                WHERE bountyId=?
            """,
                (
                    bounty["programOverview"],
                    bounty["prioritizedVulnerabilities"],
                    bounty["rewardsBody"],
                    bounty["outOfScopeAndRules"],
                    bounty["assetsBodyV2"],
                    bounty["project"],
                    bounty["maxBounty"],
                    bounty["launchDate"],
                    bounty["endDate"],
                    bounty["updatedDate"],
                    bounty["kyc"],
                    bounty["id"],
                ),
            )
            cursor.execute("DELETE FROM updates WHERE bountyId = ?", (bounty["id"],))
            cursor.execute(
                """
                INSERT INTO updates (bountyId, updatedDate)
                VALUES (?, ?)
            """,
                (
                    bounty["id"],
                    bounty["updatedDate"],
                ),
            )
            update_nested_data(cursor, bounty["id"], bounty)
    else:
        print("Inserting:", bounty["id"])
        cursor.execute(
            """
            INSERT INTO bounties (bountyId, programOverview, prioritizedVulnerabilities, rewardsBody, outOfScopeAndRules, assetsBodyV2, project, maxBounty, launchDate, endDate, updatedDate, kyc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                bounty["id"],
                bounty["programOverview"],
                bounty["prioritizedVulnerabilities"],
                bounty["rewardsBody"],
                bounty["outOfScopeAndRules"],
                bounty["assetsBodyV2"],
                bounty["project"],
                bounty["maxBounty"],
                bounty["launchDate"],
                bounty["endDate"],
                bounty["updatedDate"],
                bounty["kyc"],
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
    if "tags" in bounty:
        for tag_type, tag_values in bounty["tags"].items():
            if tag_values is not None:
                for tag_value in tag_values:
                    cursor.execute(
                        """
                        INSERT INTO tags (bountyId, tag_type, tag_value)
                        VALUES (?, ?, ?)
                        """,
                        (
                            bounty_id,
                            tag_type,
                            tag_value,
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


def create_views(cursor, views):
    for view in views:
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='view' AND name='{view}';"
        )
        if cursor.fetchone() is None:
            cursor.execute(sql_data.sql_views.CREATE_VIEW_QUICK_VIEW)


def main():
    conn, cursor = connect_db()
    try:
        process_json_files(cursor, json_directory)
        create_views(cursor, ["quick_view"])
    finally:
        conn.commit()
        conn.close()


if __name__ == "__main__":
    main()
