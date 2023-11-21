CREATE TABLE IF NOT EXISTS events(
    username String,
    post String,
    page INTEGER
) ENGINE = MergeTree()
    ORDER BY username;

CREATE MATERIALIZED VIEW

    IF NOT EXISTS events_mv
            ENGINE = MergeTree() PRIMARY KEY username
AS
(
SELECT
    username,
    count() as total_clicks,
    avg(page) as average_page
FROM events
GROUP BY username
);
