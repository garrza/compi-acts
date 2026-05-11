CREATE TABLE IF NOT EXISTS raw_data (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cleaned_data (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS keywords_data (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT,
    keywords    TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categorized_data (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT,
    keywords    TEXT,
    category    TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
