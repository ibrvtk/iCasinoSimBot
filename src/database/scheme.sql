BEGIN TRANSACTION;

-- All `*s_id` params are stored in the "id,id,id,...," format
-- All chat ids are include "-100" prefix
-- Usernames don't have the "UNIQUE" param, bc an error may occur

CREATE TABLE IF NOT EXISTS "user" (
    "id" INTEGER PRIMARY KEY,
    "username" TEXT,
    "emoji" TEXT DEFAULT "👤",
    "registration_date" INTEGER, -- int(datetime.now().timestamp())
    "language_code" TEXT DEFAULT "en",
    "items_id" TEXT,
    "stage" INTEGER DEFAULT 0,
    "is_banned" INTEGER DEFAULT 0, -- -> boolean
    "is_pro" INTEGER DEFAULT 0 -- -> boolean
);

CREATE TABLE IF NOT EXISTS "chat" (
    "id" INTEGER PRIMARY KEY,
    "username" TEXT,
    "emoji" TEXT DEFAULT "👤",
    "prefix" TEXT DEFAULT "",
    "cooldown" INTEGER DEFAULT 5,
    "is_banned" INTEGER DEFAULT 0, -- -> boolean
    "is_pro" INTEGER DEFAULT 0 -- -> boolean
);

CREATE TABLE IF NOT EXISTS "stat" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "chat_id" INTEGER,
    "user_id" INTEGER,
    "admin_level" INTEGER DEFAULT 0,
    "balance" INTEGER DEFAULT 0,
    "bonus" INTEGER,
    "secret_word" TEXT,
    "wins" INTEGER DEFAULT 0,
    "loses" INTEGER DEFAULT 0,
    "balance_without_loses" INTEGER DEFAULT 0,
    "last_play" INTEGER, -- int(datetime.now().timestamp())
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "item" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "chat_id" INTEGER,
    "name" TEXT,
    "price" INTEGER,
    "quantity" INTEGER DEFAULT -1,
    "effect" TEXT,
    "is_keepable" INTEGER DEFAULT 1, -- -> boolean
    "is_sendable" INTEGER DEFAULT 1, -- -> boolean
    FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "custom_role" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "chat_id" INTEGER,
    "name" TEXT,
    "emoji" TEXT DEFAULT "🔰",
    "admin_level" INTEGER DEFAULT 0,
    FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE CASCADE
);

COMMIT;