-- Speeds up GET /api/tasks?area=&tag= by letting Postgres use an index for
-- the JSONB containment filter (meta @> '{"tags": [...]}') instead of a
-- sequential scan across every row in the area.
CREATE INDEX IF NOT EXISTS ix_tasks_meta_gin
ON tasks
USING GIN (meta jsonb_path_ops);
