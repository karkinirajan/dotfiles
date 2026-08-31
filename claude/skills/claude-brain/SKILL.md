---
name: claude-brain
description: >
  Always-on second brain backed by a local markdown vault. Recall relevant notes
  and past sessions before working, traverse the note graph for structure
  questions, capture new knowledge at session end. Trigger on any coding,
  debugging, planning, or research task.
---

# Recall (start of work)

Run `claude-brain recall "<query>"` before debugging or building — it searches the
user's vault *and* past sessions, returning only the answering lines. Prefer it over
re-deriving knowledge the vault already holds. Add `--full` when you need a whole
section rather than the matching lines.

# Designs the user saved

If the user asks for UI or visual work that references something they liked — "like that
dashboard I saved", "the palette from that screenshot" — check the design library before
inventing a look:

```bash
claude-brain design list
claude-brain design show "<id or a description of the vibe>"
```

`show` prints the stored description and then the image's absolute path. The description
carries the palette hex, spacing scale, typography and mood; Read the image itself when
you need the part words do not carry.

# Structure questions

When the question is about how things relate rather than what they say, traverse
instead of searching. All of these accept plain English, not just exact titles:

- `claude-brain path "<A>" "<B>"` — the chain connecting two notes, typed per hop
- `claude-brain explain "<note>"` — its cluster and every neighbour by edge kind
- `claude-brain affected "<note>"` — everything that points at it, transitively
- `claude-brain map` — the whole vault as named clusters, for orientation

# Recording protocol (end of session, unprompted)

Before ending a session with meaningful work, record into the vault (location:
`claude-brain status` shows the vault path; all files are markdown):

1. **Work log** — append-or-create `Journal/YYYY-MM-DD.md` with a short dated
   section: what was done, decisions made, open ends.
2. **Solved bug / gotcha** — atomic note in `Notes/<domain>/` named after the
   symptom: Symptom / Root cause / Fix. Link related notes with `[[wikilinks]]`.
3. **Quick capture** — `claude-brain note "<text>" [-f <subfolder>]` drops a
   thought into `<subfolder>/` (default `Inbox/`) without opening an editor.
4. **Durable constraint** — `claude-brain remember "<text>" -k preference` for a
   rule that isn't note-shaped. It survives the forgetting pass; a plain prompt
   does not.

`claude-brain consolidate` reports themes that recurred across separate sessions.
Those are the strongest candidates for a real note — something hit three times in
three sessions is a fact about the work, not an incident.

Rules:
- **Organize into topical subfolders, never a flat dump** — file notes under a
  domain folder (`Notes/rust/`, `Notes/deploy/`, …); create new domain folders
  freely when none fits (3+ related notes deserve their own folder). Folder-scoped
  lookup: `claude-brain recall "<q>" -p "Notes/rust"`.
- Never edit or delete existing notes without asking. New notes are always fine.
- Keep entries atomic and searchable — titles describe the symptom or topic.
- The index updates itself; no reindex commands needed.
