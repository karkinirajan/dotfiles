# Deliberate bugs, one at a time: each (name, file, old text, new text) must make the suite fail.
# Run from the repository root (the driver checks the suite is green first; do not edit the tree while it runs;
# each `old` must occur exactly once in its file; never kill a running driver):
#   python3 tests/mutation/mutate.py tests/mutation/mutants.py -- uv run pytest -x -q --no-cov
#   python3 tests/mutation/mutate.py tests/mutation/mutants.py auth -- uv run pytest -x -q --no-cov
#   (the second form runs only the mutants whose names contain "auth")
# `--no-cov` matters: with a coverage gate on, a mutant that only lowers coverage counts as "killed" for the wrong reason.
#
# Not listed, because they cannot change behaviour (each was run once and survived):
#  - <module>: <the change> (<why nothing can observe it>)
#
# Not run: <a mutant that would start real processes or touch real services>.
#
# Copy this file to tests/mutation/mutants.py and replace the examples. One mutant per rule in code that guards something.

AUTH = "src/app/auth.py"
LIMITS = "src/app/limits.py"

M = [
    # authentication and authorization: remove a check, flip a comparison, drop an owner filter
    ("auth: the owner filter is dropped", AUTH, "return queryset.filter(owner=user)", "return queryset"),
    ("auth: any role may write", AUTH, 'if user.role != "admin":', 'if user.role != "nobody":'),
    # boundaries: off by one, changed default
    ("limits: the cap is exclusive", LIMITS, "if count >= MAX_ITEMS:", "if count > MAX_ITEMS:"),
    # fail closed: a required secret becomes optional, a minimum shrinks
    ("settings: a short secret is accepted", "src/app/settings.py", "len(secret) < 32", "len(secret) < 1"),
]
