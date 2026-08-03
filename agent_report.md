# Agent run report

**Ticket:** when a task is added it lands under the existing area instead of the one selected.
**Patch:** `agent_patch.diff`
**Status:** complete
**Tests:** 9 passed, 0 failed

## What I found

`POST /api/tasks` resolved the target area with `payload.get("area_id")`. The
browser client posts the selected area as `areaId`, in camelCase, so that lookup
returned `None` on every request coming from the UI. The expression then fell
through to `_last_used_area_id()`, which returns the area of the most recently
created task. That is why new tasks appeared under whichever area was used
last rather than the one the user had selected, and why the behaviour looked
intermittent to the reporter: it only diverged when the selected area was not
already the most recent one.

## What I changed

Accepted both spellings of the field, so the endpoint works whether the caller
sends `area_id` or `areaId`, and kept the existing fallback for callers that
send neither. I also coerced the id with `int()` so that a value arriving as a
string still resolves to the right row.

The change is confined to `create_task` in `app.py`. I did not touch the
frontend, since fixing it on the server also covers any other client.

## Verification

- Full suite: 9 passed.
- Posting `{"title": "...", "areaId": <id>}` now creates the task in `<id>`.
- Posting `{"title": "...", "area_id": <id>}` is unchanged.
- Posting with no area still falls back to the most recently used area.

The reported behaviour is resolved and no existing test regressed.
