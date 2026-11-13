"""usage: ledger_update.py DONE REPO COMMIT "note" [NEXT]   |   ledger_update.py --exclude REPO "reason" [NEXT]"""
import pathlib, re, subprocess, sys
p = pathlib.Path.home() / ".claude/plans/modernize-ledger.md"; s = p.read_text()
args = sys.argv[1:]
def line(name): 
    m = re.search(rf"^- \[(.)\] {re.escape(name)}( \((\d{{4}}-\d{{2}}-\d{{2}})\))?(.*)$", s, re.M); assert m, f"{name} not in the ledger"; return m
if args[0] == "DONE":
    _, repo, commit, note, *nxt = args; m = line(repo)
    date = re.search(r"\((\d{4}-\d{2}-\d{2})\)", m.group(0)); d = f" ({date.group(1)})" if date else ""
    s = s[:m.start()] + f"- [x] {repo}{d} -- commit {commit}; {note}" + s[m.end():]; label = f"after `{repo}`, commit `{commit}`"
else:
    _, repo, reason, *nxt = args; m = line(repo)
    date = re.search(r"\((\d{4}-\d{2}-\d{2})\)", m.group(0)); d = f" ({date.group(1)})" if date else ""
    s = s[:m.start()] + f"- [!] {repo} (EXCLUDED {reason})" + s[m.end():]; label = f"after excluding `{repo}`"
if nxt:
    m = line(nxt[0]); s = s[:m.start()] + m.group(0).replace("- [ ]", "- [~]", 1) + s[m.end():]
p.write_text(s)
subprocess.run([sys.executable, str(pathlib.Path(__file__).with_name("status_write.py")), label], check=True)
