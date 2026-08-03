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
| A |  |  |
| B |  |  |
| C |  |  |
| D (optional) |  |  |

### Task A — EXPLAIN ANALYZE, before and after

```
(paste here)
```

### Task A — what I chose not to do

### Task B — what the patch actually does

### Task B — the prompt I would have given the agent

### Task B — my own AI use on this task

### Task C — prompt, acceptance check, and my three questions

### Task D — why I fixed it where I did

### Anything that got in your way

Genuinely useful to us, and it does not count against you. If part of this was
unclear, badly specified or broken, say so.
