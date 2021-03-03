CREATE TABLE IF NOT EXISTS Users (
    id              BIGINT NOT NULL PRIMARY KEY,
    banned          BOOLEAN NOT NULL DEFAULT FALSE,
    channel_limit   INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Guilds (
    id              BIGINT NOT NULL PRIMARY KEY,
    owner_id        BIGINT NOT NULL,
    banned          BOOLEAN NOT NULL DEFAULT FALSE,
    prefix          VARCHAR(255) NOT NULL DEFAULT '!'
);

CREATE TABLE IF NOT EXISTS LinkrChannels (
    channel_name    VARCHAR(255) NOT NULL PRIMARY KEY,
    owner_id        BIGINT NOT NULL,
    extra_data      TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS DiscordChannels (
    channel_id      BIGINT NOT NULL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    adder_id        BIGINT NOT NULL,
    linkr_channel   VARCHAR(255) NOT NULL REFERENCES LinkrChannels(channel_name) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Webhooks (
    webhook         VARCHAR(255) NOT NULL PRIMARY KEY,
    channel_id      BIGINT NOT NULL REFERENCES DiscordChannels(channel_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Messages (
    c_message_id BIGINT NOT NULL PRIMARY KEY,
    message_id      BIGINT NOT NULL,
    channel_id      BIGINT NOT NULL,
    webhook_used    VARCHAR(255) NOT NULL REFERENCES Webhooks(webhook) ON DELETE CASCADE,
    content         TEXT NOT NULL
);
