// Deliberate bugs, one at a time: each must make its tests fail. Used with tests/mutation/mutate.mjs (Node projects on node:test).
// Run from the project root (do not edit the tree while it runs; each `old` must occur exactly once in `file`; never kill a running driver):
//   node tests/mutation/mutate.mjs tests/mutation/mutants.mjs [name-filter ...]
//
// Not listed, because they cannot change behaviour (each was run once and survived):
//  - <module>: <the change> (<why nothing can observe it>)
//
// Copy this file to tests/mutation/mutants.mjs and replace the examples. List BOTH the original test file and the
// edge-case test file in each mutant's `tests`, or the new tests never run and the result looks the same as before.

const auth = ["tests/auth.test.js", "tests/auth.edges.test.js"];

const m = (name, file, tests, old, replacement) => ({ name, file, tests, old, new: replacement });

export default [
  m("auth: the owner filter is dropped", "lib/auth.js", auth, "return items.filter((i) => i.owner === user.id);", "return items;"),
  m("auth: a viewer may write", "lib/auth.js", auth, 'if (user.role === "viewer") return false;', ""),
  m("limits: the cap is exclusive", "lib/limits.js", auth, "if (count >= MAX) return false;", "if (count > MAX) return false;"),
];
