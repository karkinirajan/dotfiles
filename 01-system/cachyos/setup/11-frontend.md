---
title: "11 Frontend Development"
part: "01"
chapter: "11"
topic: frontend
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 11 Frontend Development


## 11.1 Node.js via NVM

```bash
sudo pacman -S nvm
```

`03-terminal/zsh/.zshrc` automatically sources `/usr/share/nvm/init-nvm.sh`
when installed via pacman:

```bash
nvm install --lts && nvm use --lts
node -v && npm -v
```

## 11.2 Package Managers

```bash
sudo pacman -S pnpm yarn
```

## 11.3 React + Vite

```bash
pnpm create vite@latest my-react-app -- --template react-ts
cd my-react-app && pnpm install && pnpm dev
```

## 11.4 Next.js

```bash
pnpm create next-app@latest my-next-app
cd my-next-app && pnpm dev
```

## 11.5 TypeScript

```bash
pnpm add -D typescript
npx tsc --init   # Creates tsconfig.json
```

## 11.6 Tailwind CSS

```bash
pnpm add -D tailwindcss @tailwindcss/postcss postcss
npx tailwindcss init
```
