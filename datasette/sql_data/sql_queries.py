CREATE_TABLE_BOUNTIES = """
    CREATE TABLE IF NOT EXISTS bounties (
        bountyId TEXT PRIMARY KEY,
        programOverview TEXT,
        prioritizedVulnerabilities TEXT,
        rewardsBody TEXT,
        outOfScopeAndRules TEXT,
        assetsBodyV2 TEXT,
        project TEXT,
        maxBounty INTEGER,
        launchDate TEXT,
        endDate TEXT,
        updatedDate TEXT,
        kyc BOOLEAN
    )
    """
CREATE_TABLE_REWARDS = """
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

CREATE_TABLE_ASSETS = """
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

CREATE_TABLE_IMPACTS = """
CREATE TABLE IF NOT EXISTS impacts (
    impactId INTEGER PRIMARY KEY AUTOINCREMENT,
    bountyId TEXT,
    title TEXT,
    type TEXT,
    severity TEXT,
    FOREIGN KEY (bountyId) REFERENCES bounties(bountyId)
)
"""

CREATE_TABLE_TAGS = """
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bountyId TEXT,
    tag_type TEXT,
    tag_value TEXT,
    FOREIGN KEY (bountyId) REFERENCES bounties(bountyId)
)
"""

CREATE_TABLE_TARGETS = """
CREATE TABLE IF NOT EXISTS targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bountyId TEXT,
    network TEXT,
    target TEXT,
    updatedDate TEXT,
    FOREIGN KEY (bountyId) REFERENCES bounties(bountyId)
)
"""

CREATE_TABLE_UPDATES = """
CREATE TABLE IF NOT EXISTS updates (
    bountyId TEXT PRIMARY KEY,
    updatedDate TEXT,
    FOREIGN KEY (bountyId) REFERENCES bounties(bountyId)
)
"""
