# SkyTerra screening scaffold

A miniature task board: Flask, SQLAlchemy 2.0, PostgreSQL with a JSONB column,
and a vanilla-JavaScript front end with no build step. It is the same shape as
the app you would be maintaining, just very much smaller.

Nothing here is SkyTerra source code and there is no real customer data. All
50,000-plus rows are generated.

**Please read the whole of this file before you start.** Two of the four tasks
are about noticing something, and rushing costs more time than it saves.

---

## Time

- The work is scoped to **four hours**. You have a 24-hour window, and we grade
  what is committed when it closes.
- **Please record your actual hours per task at the bottom of this file.** We
  would much rather see four honest hours with a gap you did not get to than a
  suspiciously complete submission. An honest gap costs you nothing.
- Tasks A, B and C are the ones we score. **Task D is optional** and skipping
  it does not count against you. If you are short on time, skip D first, then
  the optional parts of A. Do not skip B.
- Please stop at four hours. We are not measuring stamina, and going long tells
  us less than a clear note saying what you would have done next.

## Using AI

Use it. We expect you to, and this is a seat where you would be directing
coding agents every day. Task B asks you to say which parts you generated and
how you checked them. That question is not a trap; answering it well is worth
more than pretending you wrote everything by hand.

---

## Setup

Requires Python 3.12 and Docker.

```bash
docker compose up -d                 # Postgres 16 on localhost:55432
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

python seed.py                       # ~40 seconds, loads 250,000 tasks
python app.py                        # http://localhost:5057

pytest tests -q                      # 9 passed, on a clean checkout
```

The suite runs against a **separate** `screen_test` database, so `pytest` will
not wipe the rows you seeded. If you are not using the bundled compose file,
point `TEST_DATABASE_URL` somewhere disposable.

`seed.py` is deterministic, so a timing you take now is comparable with one you
take after your change.

---

## Task A — make the slow endpoint fast, and prove it *(~60 min)*

`GET /api/tasks?area=<id>&tag=<tag>` filters on a tag held inside the `meta`
JSONB column. Against the seeded data it takes roughly **three seconds**, which
is not acceptable for a list endpoint.

It also **returns the wrong count** when a task carries the same tag twice.
About four percent of the seeded rows do, because tags arrive from more than one
source and nothing de-duplicates them. No existing test catches this.

1. Fix the performance. Put the **`EXPLAIN ANALYZE` output from before and
   after** in this file. A number, not an adjective.
2. Fix the count, and **add a test that fails on the original code and passes on
   yours**.
3. Write the **migration** for any index you add, rather than only creating it
   by hand in psql.
4. In two or three sentences, say **what you chose not to do**. We are as
   interested in the restraint as in the fix.

## Task B — review the agent's diff *(~75 min)*

This is the closest thing here to the actual job, and it is the task we weight
most heavily.

`agent_patch.diff` was produced by an AI coding agent against a real-sounding
ticket: *"when a task is added it lands under the existing area instead of the
one selected."* Its own write-up is in `agent_report.md`.

The patch applies cleanly. The full suite passes with it applied. The agent says
the bug is fixed. **It is not.** The patch fixes the reported symptom in one
path and introduces a second, quieter defect.

```bash
git apply agent_patch.diff
pytest tests -q          # still 9 passed
```

1. **Find it.** Describe what the patch actually does versus what it claims, in
   plain language.
2. **Prove it.** Write a test that *fails* with the patch applied. This is the
   deliverable that matters most.
3. **Fix it properly**, and explain why your fix belongs where you put it.
4. **Write the prompt you would have given the agent** so it would not have made
   this mistake. In full, not a description of one.
5. **Declare your own AI use** on this task: what you generated, and how you
   satisfied yourself it was right.

A green test suite is not evidence that a change is correct. That is the whole
point of this task.

## Task C — turn a real ticket into a working prompt *(~45 min)*

This is a real, unedited ticket from the SkyTerra board:

> **Agent Tracker — Make Kanban "Sort: Status" meaningful.** The Kanban toolbar
> offers Sort: Status, but the board is already split into fixed workflow-status
> columns. Sorting by status therefore does not visibly change card order: every
> card in a column already shares that status.

You are not implementing it. You are briefing an agent to.

1. **The prompt** you would hand a coding agent. Complete and copy-pasteable,
   not a sketch.
2. **The acceptance check**: what you would run or look at to know the agent
   actually did it, rather than reported that it did.
3. **Three questions** you would want answered before starting, and what you
   would assume if nobody answered them today.

This ticket has no obviously correct fix. Removing the option, redefining what
it sorts and leaving it alone are all defensible. We are reading the reasoning,
not grading the choice.

## Task D — the frontend, with no framework *(optional, ~30 min)*

In `static/app.js`, the task list rebuilds every card on each poll, so an open
status dropdown snaps shut about once a second while you are trying to use it.
Open the app, click a dropdown and wait, and you will see it.

There is no framework, no virtual DOM and no build step. That is also true of
the real SPA, so please do not add one.

1. Fix it so an open dropdown survives a refresh.
2. One paragraph on why you fixed it where you did.

---

## What to send back

A git repository with **real commit history**. The commits are evidence of how
you work; a single squashed "final" commit tells us nothing. Include this file
with the sections below filled in.

### Hours spent

| Task | Hours | Notes |
|---|---|---|
| A | 1 hr 10 min | Includes a detour debugging a false performance regression that turned out to be a stopped Flask server / curl connection timeout, not real code. |
| B | 56 min | Includes verifying the agent's root-cause claim directly in `static/app.js` rather than trusting the report, and catching a leftover unguarded line during self-review that would have made the new `try/except` silently ineffective. |
| C |  |  |
| D (optional) |  |  |

### Task A — EXPLAIN ANALYZE, before and after

**SQL query plan — before (no index on `meta`):**
```
Seq Scan on tasks  (cost=0.00..8426.00 rows=11445 width=118) (actual time=0.032..76.148 rows=12335 loops=1)
  Filter: ((meta @> '{"tags": ["backend"]}'::jsonb) AND (area_id = 3))
  Rows Removed by Filter: 237665
Planning Time: 0.406 ms
Execution Time: 76.676 ms
```

**SQL query plan — after (`ix_tasks_meta_gin` GIN index added):**
```
Bitmap Heap Scan on tasks  (cost=308.89..5666.60 rows=11445 width=118) (actual time=3.966..25.066 rows=12335 loops=1)
  Recheck Cond: (meta @> '{"tags": ["backend"]}'::jsonb)
  Filter: (area_id = 3)
  Rows Removed by Filter: 37419
  Heap Blocks: exact=4676
  ->  Bitmap Index Scan on ix_tasks_meta_gin  (cost=0.00..306.03 rows=45447 width=0) (actual time=3.463..3.463 rows=49754 loops=1)
        Index Cond: (meta @> '{"tags": ["backend"]}'::jsonb)
Planning Time: 0.531 ms
Execution Time: 25.574 ms
```

**Endpoint level, for context:** the ticket reports ~3s against the original code (Python-side filtering, no SQL change). After this fix — SQL-side filtering plus the index — `GET /api/tasks?area=3&tag=backend` returns in ~0.36–0.40s (`200`, verified over multiple runs). The gap between that and the 25.6ms SQL execution time is JSON-serializing the 12,335 matching tasks, not the query itself.

### Task A — what I chose not to do

I considered normalizing tags into a separate `tags`/`task_tags` join table, which would make duplicate tags structurally impossible and allow ordinary btree indexes instead of GIN — but that's a schema migration touching the write path and 250,000 existing rows, well beyond a ticket scoped to fixing one endpoint. I also considered a separate `COUNT(*)` query alongside a paginated task list, the more typical REST pattern, but this endpoint has no pagination today, so a second query would only duplicate work the current single query already does for free. Both are legitimate improvements I'd revisit if the endpoint's actual requirements grew to need them, not something to build speculatively now.

### Task B — what the patch actually does

The agent's diagnosis was correct: the client posts the selected area as `areaId`, but the server only checked `area_id`, so the lookup always returned `None` and silently fell back to whichever area was most recently used. I verified this directly in `static/app.js` rather than taking the report's word for it — line 90 does send `areaId`. The patch's fix for that — accepting both spellings and coercing to `int` — is genuinely correct.

What the report doesn't mention: in rewriting the area lookup, the patch also dropped the `or area.archived` clause from the validation guard. The original code rejected task creation if the area didn't exist *or* was archived; the patched version only checks for existence. That means `POST /api/tasks` against an archived area (e.g. "Legacy import") now silently succeeds, which it shouldn't — archived areas exist specifically so they can't receive new work. The full test suite still passed because no existing test ever posted to an archived area; the gap was in test coverage, not in whether the agent ran the tests.

The patch also introduced a smaller, second regression: its `int(area_id)` coercion is new (the original code never coerced the type), and an uncaught `ValueError` on malformed input now returns a raw `500` instead of the endpoint's normal clean `400`. Not part of the reported bug, but a real side effect of the rewrite worth fixing alongside it.

### Task B — the prompt I would have given the agent

```
Fix this bug: when a task is added it lands under the existing area instead of the one selected.

Before you change anything, read the full create_task function in app.py, not just the line that resolves area_id, note every check that function currently performs, and make sure your fix preserves all of them. In particular, the function currently rejects task creation both when the area doesn't exist and when the area is archived; both checks must still work after your change.

Once you've identified and fixed the root cause, write a new test for the specific bug you fixed, and then re-read your diff line-by-line asking "does every line in this diff exist because the ticket required it, or did it change incidentally while I was rewriting this code?" For any incidental change, write a test proving the old behavior it depended on is still intact. Report which lines in your diff are new behavior versus which are unrelated to the ticket, so I can review them separately.
```

### Task B — my own AI use on this task

I used Claude Code throughout this task: to lay out where the fix and test should go, with reasoning, before I wrote them myself for my own review; and to help verify the agent's own diagnosis by checking `static/app.js` directly rather than taking `agent_report.md`'s claim about the `areaId` field at face value. I wrote the actual code changes, the archived-area guard, the `int()` try/except, and the tests by hand, then had the AI review my diff against the plan. It caught a real bug I'd introduced: the original unguarded `session.get(Area, int(area_id))` line was still sitting above the new `try/except` block, so the exception handler could never actually fire. I fixed that and reran the suite to confirm 12/12 passed. The corrected prompt and patch analysis above were drafted with AI assistance, then reviewed and edited by me before finalizing.

### Task C — prompt, acceptance check, and my three questions

### Task D — why I fixed it where I did

### Anything that got in your way

Genuinely useful to us, and it does not count against you. If part of this was
unclear, badly specified or broken, say so.

**(Task A):** `docker compose exec db psql -f <path>` resolves the path inside the *container's* filesystem, not the host's. Since `migrations/` isn't mounted the way `initdb/` is, running `docker compose exec db psql -f migrations/0001_add_tasks_meta_gin_index.sql` fails with "No such file or directory", which reads like a broken migration but is really just a path-resolution gotcha. Piping the file in via stdin instead (`docker compose exec -T db psql -U screen -d screen < migrations/0001_....sql`) works. Worth a one-line note in the README's setup section for anyone applying a migration by hand.

**(Task B):** the README's `git apply agent_patch.diff` instructions don't say whether Task B is meant to be worked against a clean checkout or cumulatively on top of whatever earlier tasks already changed. In my case it applied cleanly on top of the Task A changes since they touch different functions, but that's incidental rather than guaranteed by the setup, a candidate whose Task A changes happened to touch `create_task` could hit a real conflict through no fault of their own. Also unclear: whether the "test fails with the patch applied" evidence is expected to survive as a commit in the history, or just as pasted output in this file. I treated it as transient, the same way Task A's `EXPLAIN ANALYZE` numbers are evidence rather than code, but the instructions don't say either way.
