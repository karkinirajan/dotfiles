#!/usr/bin/env node
// Mutation check: apply deliberate bugs one at a time and require the unit tests to fail for each.
//
//   node tests/mutation/mutate.mjs tests/mutation/mutants.mjs [name-filter ...]
//
// The mutants file's default export is a list of { name, file, tests, old, new }: `old` must occur exactly once in `file`, and
// `tests` are the test files that exercise it. Each group of tests must pass unmutated first (a failing baseline would make every
// mutant look killed). Files are restored in a `finally` block, so do not kill a running check and do not edit the tree while it
// runs. Exit status: 0 all killed, 1 a survivor or a bad pattern, 2 a failing baseline.
import { spawnSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const TIMEOUT_MS = 180_000;
const [spec, ...filters] = process.argv.slice(2);
if (!spec) {
  console.error("usage: node tests/mutation/mutate.mjs <mutants file> [name-filter ...]");
  process.exit(2);
}

const all = (await import(pathToFileURL(resolve(spec)).href)).default;
const mutants = filters.length ? all.filter((m) => filters.some((f) => m.name.includes(f))) : all;

/** Run the given test files; returns the exit status (a timeout counts as a failure). */
function runTests(tests) {
  const done = spawnSync("node", ["--test", ...tests], { encoding: "utf8", timeout: TIMEOUT_MS });
  return { status: done.status ?? 124, output: `${done.stdout ?? ""}${done.stderr ?? ""}` };
}

const originals = new Map(mutants.map((m) => [m.file, readFileSync(m.file, "utf8")]));

const groups = new Map(mutants.map((m) => [m.tests.join(" "), m.tests]));
for (const [label, tests] of groups) {
  const { status, output } = runTests(tests);
  if (status !== 0) {
    console.log(`BASELINE FAILS for ${label}: the tests must pass before any mutation.\n${output.split("\n").slice(-15).join("\n")}`);
    process.exit(2);
  }
}
console.log("baseline green");

const problems = [];
try {
  for (const m of mutants) {
    const source = originals.get(m.file);
    const count = source.split(m.old).length - 1;
    if (count !== 1) {
      console.log(`PATTERN? (${count}x) ${m.name}`);
      problems.push(m.name);
      continue;
    }
    writeFileSync(m.file, source.replace(m.old, () => m.new));
    const killed = runTests(m.tests).status !== 0;
    console.log(`${killed ? "killed  " : "SURVIVED"} ${m.name}`);
    if (!killed) problems.push(m.name);
    writeFileSync(m.file, source);
  }
} finally {
  for (const [file, content] of originals) writeFileSync(file, content);
}

const restored = [...originals].every(([file, content]) => readFileSync(file, "utf8") === content);
console.log(`\n${mutants.length - problems.length}/${mutants.length} killed; restored: ${restored}`);
process.exit(problems.length ? 1 : 0);
