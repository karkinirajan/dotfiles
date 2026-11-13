"""Regenerate the single status file ~/modern-repo-status.md (Done | Todo | Skipped) from the ledger.
usage: status_write.py "<label>"      (ledger_update.py calls this after every change; status_md.py is an alias)"""
import datetime, pathlib, re, sys
home = pathlib.Path.home()
rows = re.findall(r"^- \[(.)\] (\S+)(.*)$", (home / ".claude/plans/modernize-ledger.md").read_text(), re.M)
done = [n for m, n, _ in rows if m == "x"]
todo = [(n, m == "~") for m, n, _ in rows if m in (" ", "~")]
skipped = [(n, rest) for m, n, rest in rows if m == "!"]
label = sys.argv[1] if len(sys.argv) > 1 else "updated"
cell = lambda i, items: f"{i + 1}. {items[i]}" if i < len(items) else ""
todo_cells = [f"{n} (in progress, nothing committed yet)" if active else n for n, active in todo]
skip_cells = [n for n, _ in skipped]
active = [n for n, a in todo if a]
first = todo[0][0] if todo else None
state = (f"`{first}` is in progress." if active else (f"The next repository is `{first}`." if first else "Nothing is left."))
out = ["# Repository modernization status", "",
       f"As of {datetime.date.today().isoformat()} ({label}): **{len(done)} done**, **{len(todo)} todo**" + (f", **{len(skipped)} skipped**" if skipped else "") + f". {state}", "",
       "Repositories are processed in the order of the ledger (first-commit date, with the owner's re-orderings). Work is on local `chore/modernize` branches; nothing has been pushed.", ""]
out += ["| Done | Todo | Skipped |", "|---|---|---|"] if skipped else ["| Done | Todo |", "|---|---|"]
for i in range(max(len(done), len(todo_cells), len(skip_cells))):
    out.append(f"| {cell(i, done)} | {cell(i, todo_cells)} |" + (f" {cell(i, skip_cells)} |" if skipped else ""))
if skipped:  # only while something is skipped: the section and the note about forks
    out += ["", "## Why each one was skipped", ""]
    for n, rest in skipped:
        r = re.sub(r"\s*\(\d{4}-\d{2}-\d{2}\)\s*$", "", rest.strip()); r = r[1:-1] if r.startswith("(") and r.endswith(")") else r
        out.append(f"* `{n}`: {r}")
    out += ["", "Forked repositories are skipped unless the task names them."]
out.append("")
(home / "modern-repo-status.md").write_text("\n".join(out))
print(f"written ~/modern-repo-status.md: done={len(done)} todo={len(todo)} (incl. {len(active)} in progress) skipped={len(skipped)}")
