---
title: "11 Frontend Development"
part: "01"
chapter: "11"
topic: frontend
versions: [nodejs, npm, nvm, pnpm, yarn, fe-next, fe-typescript, fe-tailwindcss]
last_verified: 2026-10-29
status: current
sources:
  - https://nodejs.org/en/about/previous-releases
  - https://pnpm.io/
  - https://vite.dev/guide/
  - https://nextjs.org/docs
---

# 11 Frontend Development

## 11.1 Node.js via NVM

Node 26 "Lithium" became LTS on 2026-10-28 (v26.13.0, bundled npm 11.20.0); Node 24 "Krypton" moved to Maintenance on 2026-10-20 (supported to 2028-04-30); Node 22 ends 2027-04-30. Arch `nodejs` is <!-- v:nodejs -->26.12.1<!-- /v --> (without npm) and Arch `npm` is <!-- v:npm -->12.2.1<!-- /v -->, which blocks dependency install scripts by default (`allowScripts`) and sets `allow-git`/`allow-remote` to `none`. `nvm` shadows the system `node` in interactive shells; non-interactive scripts see the pacman Node.

```bash
sudo pacman -S --needed nvm
```

`03-terminal/zsh/.zshrc` sources `/usr/share/nvm/init-nvm.sh` when nvm is installed via pacman (Arch's `nvm` is <!-- v:nvm -->0.40.8<!-- /v -->; the upstream install script is not needed):

```bash
nvm install --lts && nvm use --lts      # resolves to Node 26 since 2026-10-28
nvm install 24                          # keep Krypton (Maintenance LTS) for projects that pin it
nvm alias default 'lts/*'               # default to the newest LTS
node -v && npm -v
```

Label: `machine-only` (nvm resolution inferred from the nvm README and nodejs.org's release index; nvm itself was not run). Arch's `/usr/share/nvm/init-nvm.sh` (read on the host) sets `NVM_DIR` to `$XDG_CONFIG_HOME/nvm` or `~/.nvm`, links `nvm.sh` and `nvm-exec` into it, then sources `nvm.sh` and the bash completion.

## 11.2 Package managers

```bash
sudo pacman -S --needed pnpm yarn
```

`pnpm` is <!-- v:pnpm -->12.15.0<!-- /v --> from pacman (upstream 12.16.1): a native binary, no Node dependency. In pnpm 12 the global bin directory is `$PNPM_HOME/bin`, and it must be on `PATH` or `pnpm add -g` fails with `ERR_PNPM_GLOBAL_BIN_DIR_NOT_IN_PATH` (the tracked `.zshrc` adds it). Build scripts are blocked until approved (`pnpm approve-builds`, `allowBuilds` in `pnpm-workspace.yaml`), and new releases are held for 1440 minutes (`minimumReleaseAge`). On Arch update with pacman: `pnpm self-update` installs a copy under `$PNPM_HOME/bin` that shadows the pacman one.

The pacman `yarn` package is **Yarn Classic 1.22.22**. For Yarn 4 (Berry) use Corepack, which Node 25+ no longer bundles: `sudo pacman -S corepack`, `corepack enable`, then `yarn set version stable` in the project.

## 11.3 React + Vite

```bash
pnpm create vite@latest my-react-app --template react-ts
cd my-react-app && pnpm install && pnpm dev
```

Under pnpm 12 a `--` before `--template` makes the scaffolder ignore the template and produce vanilla TypeScript; only npm needs the `--`. Vite is 8.x (Rolldown-based, Node 20.19+ or 22.12+); `create-vite` 9.3 scaffolds React 19.3 and TypeScript ~7.0.

## 11.4 Next.js

Next.js <!-- v:fe-next -->16.4.3<!-- /v --> is current. **Never deploy `next` below 16.4.1**: 16.4.0 contains a Critical unauthenticated RCE in `use cache` functions and a Critical RCE in Image Optimization. Security releases are monthly; the next is scheduled for 2026-11-03. The Node 20.9+ floor applies; `next build` no longer runs the linter.

```bash
pnpm create next-app@latest my-next-app --yes
cd my-next-app && pnpm dev
```

## 11.5 TypeScript

`typescript@latest` on npm is now 7.0.2 (the native compiler: no JavaScript API, `baseUrl` and `node10` resolution removed). `typescript-eslint` still requires TypeScript below 6.1, so with ESLint pin 6.x for tooling:

```bash
pnpm add -D typescript@6
npx tsc --init   # tsconfig.json: strict, module nodenext, noUncheckedIndexedAccess
```

A global `typescript-language-server` needs `typescript@6` beside it (TypeScript 7 ships no `tsserver.js`); the pacman packages `typescript` (6.0.3) and `typescript-language-server` cover that. For the dual-compiler setup used by the frontend skill see its version policy.

## 11.6 Tailwind CSS

Tailwind <!-- v:fe-tailwindcss -->4.3.3<!-- /v --> is CSS-first: there is no `tailwind.config.js` and no `npx tailwindcss init` (the `tailwindcss` package has no executable in v4; the CLI is `@tailwindcss/cli`).

```bash
pnpm add -D tailwindcss @tailwindcss/postcss postcss
```

```js
// postcss.config.mjs
export default { plugins: { "@tailwindcss/postcss": {} } };
```

```css
/* src/app.css */
@import "tailwindcss";
```

With Vite use the plugin instead: `pnpm add -D tailwindcss @tailwindcss/vite` and add `tailwindcss()` from `@tailwindcss/vite` to the Vite `plugins` array.

## Verify

```bash
node --version
pnpm --version
```

Expected: Node <!-- v:nodejs -->26.12.1<!-- /v --> (pacman) or 26.13.0 under `nvm install --lts`; pnpm <!-- v:pnpm -->12.15.0<!-- /v -->.

## Sources

- [Node.js releases](https://nodejs.org/en/about/previous-releases) and the release schedule
- [pnpm installation](https://pnpm.io/installation), [supply-chain settings](https://pnpm.io/supply-chain-security)
- [Next.js security releases](https://nextjs.org/blog)
- Ledger: cluster C4 and C9 in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
