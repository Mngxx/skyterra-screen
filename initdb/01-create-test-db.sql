-- A separate database for the test suite, so running pytest does not wipe the
-- 250,000 rows you seeded for the task A timings.
CREATE DATABASE screen_test OWNER screen;
