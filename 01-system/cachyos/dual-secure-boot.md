---
title: Dual boot with Secure Boot (CachyOS, Windows 11, Limine)
part: "01"
chapter: dual-secure-boot
topic: dual-secure-boot
last_verified: 2026-11-01
status: current
---

# Dual boot with Secure Boot: CachyOS and Windows 11 under one Limine menu

The complete, ordered record of how this workstation went from an unused USB stick to a Windows 11 + CachyOS dual boot with UEFI Secure Boot **on for both systems** and **Limine as the only bootloader**, listing both. Every command below is one that was actually run. The helper scripts are embedded in the [appendix](#appendix-the-scripts), so this single file is enough to repeat the whole procedure.

| Section | What it answers |
|---|---|
| [1. Introduction](#1-introduction) | What is built, on what, and what is out of scope |
| [2. Why](#2-why) | The reasoning behind each design choice |
| [3. Tools and utilities](#3-tools-and-utilities) | What was used for what |
| [4. How it works](#4-how-it-works) | The boot chain and what every script does |
| [5. Exact steps, in order](#5-exact-steps-in-order) | Zero to finished, with expected output |
| [6. Final state achieved](#6-final-state-achieved) | What the machine looks like at the end, and what was verified |
| [7. Maintenance and recovery](#7-maintenance-and-recovery) | Day-two rules and how to back out |
| [8. Gotchas met along the way](#8-gotchas-met-along-the-way) | Things that went wrong or surprised |
| [Appendix: the scripts](#appendix-the-scripts) | The four scripts, complete |

## 1. Introduction

### Goal

- Windows 11 Pro installed next to CachyOS on the same NVMe, **sharing the one EFI System Partition**.
- UEFI Secure Boot **enabled**, with both systems booting under it.
- **Limine as the single boot manager**; its menu lists CachyOS and Windows 11.

### Scope

| Part | What | Where |
|---|---|---|
| A | Build a Windows 11 installer USB stick from Linux | [Part A](#part-a-build-the-windows-11-installer-from-linux) |
| B | Replace the firmware's keys, sign Limine, lock its config, list Windows, switch Secure Boot on | [Part B](#part-b-secure-boot-with-limine-as-the-single-bootloader) |
| C | Remove the temporary files | [Part C](#part-c-clean-up) |

Running Windows' own setup wizard, and shrinking the Linux partition to make room for it, were done by hand and are not scripted here. The chapter records only the layout they produced.

### Tested on

| Component | Value |
|---|---|
| OS | CachyOS (Arch), kernel `linux-cachyos` 7.3.0-4 |
| Boot mode | UEFI |
| Board | Gigabyte B550 GAMING X V2 (firmware setup entered with `Del`), TPM present |
| Disk | One NVMe. Shared 4 GiB FAT32 EFI partition mounted at `/boot` with `fmask=0077` (root-only). Btrfs root (`@`) and `@home` |
| Bootloader | Limine 12.9.4-1, `limine-mkinitcpio-hook` 1.40.0-1, `limine-snapper-sync` 1.32.1-1 |
| Secure Boot tooling | `sbctl` 0.18 |
| Windows image tooling | `wimlib` 1.14.5 |
| Windows | Windows 11, multi-edition x64, en-US, build 26300.9457 (Microsoft's download page labelled the release 26H2) |

### How this differs from the single-OS profile

[`fresh-setup.md`](../../fresh-setup.md) describes the single-OS profile: Secure Boot off, one CachyOS menu entry, no Windows entry. This chapter is the dual-boot variant and differs in two ways:

1. **Secure Boot is on** (keys generated for this machine, never copied from another host).
2. **The Limine menu has a `Windows 11` entry**, added with `limine-entry-tool --add-efi`.

`FIND_BOOTLOADERS="no"` is unchanged, so no generic fallback loader entries appear in the menu.

## 2. Why

1. **The requirement.** Secure Boot on for both operating systems, and one bootloader that lists both.
2. **Why build the installer this way.** Rufus is Windows-only. WoeUSB-ng is AUR-only and heavy. Ventoy is a multiboot loader, not a real flash. A scripted GPT + FAT32 layout uses stock packages, copies Microsoft's files unchanged (so the Microsoft-signed boot files stay valid under Secure Boot), and boots on UEFI.
3. **Why `install.wim` is split.** UEFI firmware reads FAT, and FAT32 cannot hold a file of 4 GiB or more. This build's `install.wim` was 8,155,984,950 bytes, so it is split into `install*.swm` parts.
4. **Why the ISO is fetched through a browser.** A scripted call to Microsoft's download API was rejected (`ErrorSettings.SentinelReject`). That is an anti-automation check, and it is not worked around. A normal browser session through the official page works.
5. **Why new Secure Boot keys.** The firmware held custom keys created before this install (Platform Key dated 2026-02-05) whose private halves no longer existed, so nothing could be signed that the firmware would trust. The BIOS option to restore factory keys would reinstall keys nobody here can sign with. The firmware is therefore cleared to Setup Mode and fresh keys are enrolled.
6. **Why Microsoft's certificates are enrolled too.** The firmware must keep trusting Microsoft-signed code. The Windows boot manager is signed by `Microsoft Windows Production PCA 2011`, and enrolling Microsoft's set also keeps option ROMs trusted.
7. **Why Limine's config checksum is enrolled.** Per Limine's own documentation, without an enrolled checksum Limine treats Secure Boot as inactive and applies none of the hardening. Enrolling it is the explicit opt-in to enforcement.
8. **Why no signed kernels or UKIs.** With the checksum enrolled and Secure Boot active, Limine requires a BLAKE2b hash on every kernel and initramfs path it loads itself. `ENABLE_VERIFICATION=yes` (the tool's default) writes those hashes. The one exception is EFI chainloading: Windows needs no hash because the firmware verifies its Microsoft signature.
9. **Why `--add-efi` for Windows.** `FIND_BOOTLOADERS` only detects systemd-boot, rEFInd and the default EFI loader. `limine-entry-tool --add-efi` is the supported way to add a top-level EFI entry, and the tool then owns and preserves it.
10. **Why the fallback loader is kept identical.** `\EFI\BOOT\BOOTX64.EFI` was a byte-identical copy of Limine. Left alone it would be unsigned (the firmware rejects it under Secure Boot) and stale after every config change (a stale checksum makes Limine panic).

## 3. Tools and utilities

| Tool | Used for |
|---|---|
| `lsblk`, `udevadm`, `efibootmgr` | Identify the stick and the system disk; read UEFI boot entries |
| `/sys/firmware/efi/efivars`, `od`, `python3 -I`, `openssl` | Read `SecureBoot`, `SetupMode`, `PK`, `KEK`, `db` without root |
| Microsoft download page, Chromium driven by Playwright | Obtain the signed ISO link |
| `curl`, `sha256sum` | Download (resumable) and integrity-check the ISO |
| `7z` | Unpack the ISO as a normal user |
| `wimlib-imagex` (package `wimlib`) | Inspect, split and verify the Windows image |
| `parted`, `wipefs`, `dd`, `mkfs.vfat`, `mount`, `cp`, `diff` | Lay out, fill and verify the stick (inside the flash script) |
| `sbctl` | Create keys, enroll them in firmware, sign binaries, report status |
| `limine`, `limine enroll-config` | Embed the `limine.conf` BLAKE2b checksum into the Limine EFI binary |
| `limine-entry-tool` | Manage menu entries (`--add-efi`) |
| `limine-update`, `limine-enroll-config`, `limine-install` | Regenerate boot files, enroll the config checksum, sign Limine |
| `limine-mkinitcpio-hook` hooks in `/etc/boot/hooks/pre.d` and `post.d` | Re-enroll and re-sign automatically on every kernel or config change |
| `b2sum` | BLAKE2b, the hash Limine uses for the config and for file paths |

`limine-update` is `limine-install --no-efi-register` followed by `limine-mkinitcpio`.

## 4. How it works

### 4.1 The installer stick

- The firmware reads only FAT, so the stick gets a GPT table with one FAT32 partition (label `WIN11`, type `msftdata`).
- The ISO is unpacked with `7z` as a normal user, and its files are copied unchanged.
- `install.wim` is replaced by `install.swm`, `install2.swm`, `install3.swm` (3800 MiB parts), which Windows Setup reads as one image.
- `flash-win11-usb.sh` finds the stick by its serial number (never by a remembered `/dev/sdX` letter), refuses anything mounted as a system path, asks for a typed confirmation, and finally re-reads the stick from the device (caches dropped) and diffs it against the source tree.

### 4.2 The Secure Boot chain of trust

```text
UEFI firmware, Secure Boot ON, User Mode
  PK  = your Platform Key            (made by sbctl; private key in /var/lib/sbctl)
  KEK = your Key Exchange Key + Microsoft KEK CA 2011 + Microsoft KEK 2K CA 2023
  db  = your Database Key + five Microsoft certificates
   |
   +-- loads \EFI\limine\limine_x64.efi         signed with your db key
   |     |  carries the BLAKE2b checksum of /boot/limine.conf
   |     |  checks limine.conf against it, then every kernel/initramfs by its #hash
   |     +-- "CachyOS"     -> linux-cachyos, loaded and hash-checked by Limine
   |     +-- "Windows 11"  -> asks the firmware to load \EFI\Microsoft\Boot\bootmgfw.efi
   |                          firmware checks Microsoft's signature against db
   |
   +-- \EFI\BOOT\BOOTX64.EFI = identical copy of the signed Limine (fallback path)
```

When Secure Boot is active **and** a config checksum is enrolled, Limine enforces (from its `USAGE.md`):

- The config is verified against the checksum on every boot; a mismatch panics.
- Every file path needs a `#<blake2b>` suffix, except EFI chainloads, which the firmware verifies.
- The config editor and the UEFI-shell key are disabled, and `hash_mismatch_panic` is forced on.

### 4.3 What each script does

**`flash-win11-usb.sh`**

- Validates the staged tree (`bootmgr`, `efi/boot/bootx64.efi`, `boot.wim`, `setup.exe`, an `install.swm` or `install.wim`, no file at or above the FAT32 limit).
- Resolves the stick by `ID_SERIAL_SHORT`, requires a removable USB device and enough size.
- Aborts if any partition of it is mounted at `/`, `/boot`, `/home`, `/var`, `/usr`, `/etc`, `/srv` or `/root`.
- Wipes, partitions (GPT, one FAT32 partition), copies, syncs, drops caches, remounts read-only and runs `diff -rq`. `--dry-run` prints the plan and changes nothing.

**`sb-phase1-prepare.sh`** (root, safe to re-run)

- Installs `sbctl`.
- Backs up the whole ESP, `/etc/default/limine` and a tarball of the new signing keys into `/root/secureboot-backup`.
- Runs `sbctl create-keys` (skipped if keys exist), prints `sbctl status`, the Limine config, the ESP file list and binary hashes.
- Changes nothing about how the machine boots.

**`sb-phase3-enroll.sh`** (root; `--dry-run` supported)

- Preflight, before any change: UEFI, `sbctl` and keys present, `SetupMode=1`, `SecureBoot=0`, all needed files exist, no second `limine.conf` on the ESP. Backs up the config and `/etc/default/limine`.
- Enrolls your keys plus Microsoft's: `sbctl enroll-keys --microsoft`.
- Sets `ENABLE_ENROLL_LIMINE_CONFIG="yes"` in `/etc/default/limine`.
- Adds the Windows entry: `limine-entry-tool --add-efi "Windows 11" /boot/EFI/Microsoft/Boot/bootmgfw.efi`.
- Runs `limine-update`, which rebuilds the initramfs, writes kernel and initramfs hashes into `limine.conf`, enrolls the config checksum into Limine and signs it.
- Installs the hook `/etc/boot/hooks/post.d/95-sync-limine-fallback`, which copies the signed Limine over `\EFI\BOOT\BOOTX64.EFI` after every update.
- Verifies: both Limine copies signed and identical, Windows entry present, menu order, and no path without a hash. On any problem it exits 1 and says not to enable Secure Boot.

**`sb-verify.sh`** (root, read-only)

- Checks that the checksum inside both Limine binaries equals the current `limine.conf` (Limine stores it as ASCII hex).
- Recomputes the BLAKE2b of every kernel, initramfs and module path in `limine.conf` and compares.
- Checks both Limine binaries are signed, and prints the firmware key state.
- Ends with `All checks passed.` or `PROBLEMS FOUND`.

### 4.4 What changes on the machine

| Where | Change |
|---|---|
| Firmware variables | `PK`, `KEK`, `db` replaced (your keys + Microsoft's) |
| `/var/lib/sbctl/` | New signing keys (private) |
| `/root/secureboot-backup/` | ESP backup, config backups, keys tarball |
| `/etc/default/limine` | Adds `ENABLE_ENROLL_LIMINE_CONFIG="yes"` |
| `/boot/limine.conf` | `Windows 11` entry added; hashes regenerated |
| `/boot/EFI/limine/limine_x64.efi`, `/boot/EFI/BOOT/BOOTX64.EFI` | Config checksum enrolled, signed, identical |
| `/boot/vmlinuz-linux-cachyos` | Signed by `sbctl`'s mkinitcpio post hook (harmless; Limine checks the hash) |
| `/etc/boot/hooks/post.d/95-sync-limine-fallback` | New hook |
| Packages | `sbctl` added; `wimlib` added for Part A and removed in Part C |

## 5. Exact steps, in order

### Conventions

- Scripts live in `~/secureboot-setup/`. **Not `/tmp`**: it is cleared on reboot, and Part B reboots twice.

  ```bash
  mkdir -p ~/secureboot-setup
  ```

  Save the four scripts from the [appendix](#appendix-the-scripts) there under their own names.
- Every downloaded or extracted tree goes in its own new, empty directory. Scripts are never run from inside one.
- Commands starting with `sudo` are run by you in your own terminal.

### Part A: build the Windows 11 installer from Linux

**A1. Install `wimlib`.**

```bash
sudo pacman -S --needed wimlib
```

**A2. Identify the pendrive (read-only).**

```bash
lsblk -o NAME,PATH,SIZE,TYPE,TRAN,RM,HOTPLUG,FSTYPE,LABEL,MODEL,VENDOR,MOUNTPOINTS
udevadm info --query=property --name=/dev/sda | grep -E '^(ID_MODEL|ID_VENDOR|ID_SERIAL_SHORT|ID_BUS)='
```

Pick the disk with `TRAN=usb` and `RM=1` that is unmounted; the system disk is the NVMe. Here it was a 15.2 GiB stick at `/dev/sda`. **Write down `ID_SERIAL_SHORT`**: the flash script keys on it.

**A3. Get the ISO.** Save it into a new empty directory.

```bash
mkdir -p ~/Downloads/win11-iso
```

*Route 1 (any browser, simplest).* Open `https://www.microsoft.com/en-us/software-download/windows11`, choose **Windows 11 (multi-edition ISO for x64 devices)**, language **English (United States)**, click **64-bit Download**, and save into `~/Downloads/win11-iso/`.

*Route 2 (what was done).* Chromium, unmodified and visible, driven with Playwright, performed the same clicks and read the signed link from the page. Page elements used: `select#product-edition` = `3813`, button `#submit-product-edition`, `select#product-languages` = `English (United States)`, button `#submit-sku`, then the anchor matching `a[href*=".iso"]`. The link is valid for about 24 hours and was then fetched with `curl`:

```bash
ISO=~/Downloads/win11-iso/Windows11_Client_x64_en-us_26300_9457.iso
curl -sI "$SIGNED_URL" | grep -iE '^(HTTP|content-length|accept-ranges)'   # 200, 9047330816, bytes
curl -fL --retry 8 --retry-delay 5 --retry-all-errors -C - --no-progress-meter -o "$ISO" "$SIGNED_URL"
```

Do not script Microsoft's API directly: it answers `ErrorSettings.SentinelReject`.

**A4. Verify the download.**

```bash
stat -c '%s bytes' "$ISO"                       # 9047330816 for this build
sha256sum "$ISO" | tee ~/Downloads/win11-iso/SHA256.txt
```

For this build the SHA-256 was `bd4307df32bc8af33b39ccecb1174aeb345386630f89a2b86c7a4e36b55ea650`. It matched the "English 64-bit" row of the hash table on Microsoft's download page (newer releases will differ; compare with the table on the page you downloaded from).

**A5. Unpack and inspect (no root).**

```bash
STAGE=~/Downloads/win11-stage; mkdir "$STAGE"
7z x -y -bso0 -bsp0 -o"$STAGE" "$ISO"
wimlib-imagex info "$STAGE/sources/install.wim" | grep -E '^(Image Count|Index|Name|Edition ID|Build|Service Pack Build)'
```

Expect 11 images; **Windows 11 Pro is index 6** (Edition ID `Professional`), build 26300, service pack build 9457.

**A6. Split `install.wim` and verify the split.**

```bash
cd "$STAGE/sources"
wimlib-imagex split install.wim install.swm 3800
wimlib-imagex verify install.swm --ref="install*.swm"      # must end: "install.swm" was successfully verified.
rm -- install.wim
cd ~
find "$STAGE" -type f -size +4294967294c                    # must print nothing
```

Result here: `install.swm` 3,984,090,821 bytes, `install2.swm` 3,964,468,645, `install3.swm` 139,734,478; whole tree 8,973,997,759 bytes.

**A7. Flash the stick.** Put the serial from A2 into `EXPECT_SERIAL` in `flash-win11-usb.sh`, then dry-run first.

```bash
bash ~/secureboot-setup/flash-win11-usb.sh --dry-run "$STAGE"
sudo bash ~/secureboot-setup/flash-win11-usb.sh "$STAGE"
```

The dry run must name your stick and print the plan. The real run shows the target and asks you to type `ERASE <serial>`. It ends with `VERIFY OK: every file on the pendrive matches the stage tree.`

**A8. Install Windows (by hand, not scripted).** Boot the stick from the firmware boot menu in UEFI mode. At the edition screen pick **Windows 11 Pro**, and choose "I don't have a product key" if asked. Install into the free space on the NVMe. The layout afterwards (Linux partition shrunk from 472.9 GiB to 322.9 GiB beforehand, Windows reusing the existing EFI partition):

```text
nvme0n1p1     4G  vfat   EFI System            /boot   shared by both systems
nvme0n1p2 322.9G  btrfs  Linux filesystem      /
nvme0n1p3    16M         Microsoft reserved
nvme0n1p4 149.1G  ntfs   Microsoft basic data  (Windows)
nvme0n1p5   892M  ntfs   Windows recovery environment
```

Windows Setup adds `\EFI\Microsoft\Boot\bootmgfw.efi` to the shared EFI partition and a `Windows Boot Manager` firmware entry.

### Part B: Secure Boot with Limine as the single bootloader

**B1. Baseline, read-only (no root).**

```bash
lsblk -o NAME,SIZE,TYPE,TRAN,FSTYPE,PARTTYPENAME,LABEL,MOUNTPOINTS
efibootmgr -v
G=8be4df61-93ca-11d2-aa0d-00e098032b8c
for v in SecureBoot SetupMode; do printf '%s=' "$v"; od -An -tu1 -j4 -N1 /sys/firmware/efi/efivars/$v-$G; done
cat /etc/default/limine
```

Observed: one shared ESP; the Windows partition shows plain `ntfs` (not `BitLocker`); boot order `Limine`, `Windows Boot Manager`, `UEFI OS` (the fallback path); `SecureBoot=0`, `SetupMode=0` (keys present, Secure Boot off); `/etc/default/limine` held `ESP_PATH`, `KERNEL_CMDLINE[default]`, `BOOT_ORDER="linux-cachyos"` and `FIND_BOOTLOADERS="no"`.

List the certificates already in the firmware (no root):

```bash
python3 -I - <<'EOF'
import os, struct, subprocess, tempfile
EV = '/sys/firmware/efi/efivars/'
X509 = bytes.fromhex('a159c0a5e494a74a87b5ab155c2bf072')   # EFI_CERT_X509_GUID
for var in ('PK', 'KEK', 'db'):
    names = [f for f in os.listdir(EV) if f.startswith(var + '-')]
    if not names:
        print(f'[{var}] not present')
        continue
    data = open(EV + names[0], 'rb').read()[4:]               # skip the 4 attribute bytes
    i, subjects = 0, []
    while i + 28 <= len(data):
        sig_type = data[i:i + 16]
        list_size, hdr_size, sig_size = struct.unpack('<III', data[i + 16:i + 28])
        body = data[i + 28 + hdr_size:i + list_size]
        for j in range(0, len(body), sig_size):
            if sig_type == X509:
                with tempfile.NamedTemporaryFile(suffix='.der') as t:
                    t.write(body[j + 16:j + sig_size])
                    t.flush()
                    out = subprocess.run(['openssl', 'x509', '-inform', 'DER', '-in', t.name, '-noout', '-subject'],
                                         capture_output=True, text=True).stdout
                subjects.append(out.strip().removeprefix('subject=').split('CN=')[-1])
        i += list_size
    print(f'[{var}] {len(subjects)} certs: ' + '; '.join(subjects))
EOF
```

Observed before the change: `PK` = one `Platform Key`; `KEK` = `Key Exchange Key` plus the two Microsoft KEK CAs; `db` = `Database Key` plus five Microsoft certificates. The Platform Key dated from 2026-02-05, before this OS install, and `/var/lib/sbctl` did not exist, so its private key was gone. That is why Setup Mode is needed (step B4).

What `sbctl` 0.18 will enroll with `--microsoft` (the names embedded in its binary): `Microsoft Corporation KEK 2K CA 2023`, `Microsoft Corporation KEK CA 2011`, `Microsoft Corporation UEFI CA 2011`, `Microsoft Option ROM UEFI CA 2023`, `Microsoft UEFI CA 2023`, `Microsoft Windows Production PCA 2011`, `Windows UEFI CA 2023`. The Windows boot manager inside `install.wim` is signed by `Microsoft Windows Production PCA 2011` (chain to `Microsoft Root Certificate Authority 2010`), so it is covered. That CA certificate's validity ended on 2026-10-19; UEFI firmware does not check expiry, so it still validates.

**B2. Phase 1: prepare.**

```bash
sudo bash ~/secureboot-setup/sb-phase1-prepare.sh
```

Installs `sbctl`, writes the backups to `/root/secureboot-backup`, creates the keys, prints the Limine state. Afterwards `sbctl status` shows `Installed: ✓`, `Setup Mode: ✓ Disabled`, `Secure Boot: ✗ Disabled`, `Vendor Keys: microsoft`. In this run `limine_x64.efi` and `BOOTX64.EFI` had identical SHA-256, confirming the fallback is a plain copy.

**B3. Copy the signing keys off this disk.** Copy `/root/secureboot-backup/sbctl-keys-*.tar.zst` to media that is not this machine's disk. The previous keys were lost with a reinstall, which is the reason B4 was needed.

**B4. Firmware: clear the keys to enter Setup Mode.** Reboot and enter the firmware setup (`Del`). Find the Secure Boot settings (on this board under the Boot section; the exact menu names were not recorded, and wording varies by firmware). If there is a Secure Boot Mode option, set it to Custom. In Key Management choose the option that **clears or deletes all keys** ("Reset to Setup Mode" or similar). **Do not** choose "Restore Factory Keys" or "Install default Secure Boot keys". Leave Secure Boot disabled, save, exit, and boot CachyOS through Limine as usual. Confirm:

```bash
od -An -tu1 -j4 -N1 /sys/firmware/efi/efivars/SetupMode-8be4df61-93ca-11d2-aa0d-00e098032b8c   # 1
sbctl status                                                                                     # Setup Mode: Enabled
```

**B5. Phase 3: enroll, list Windows, sign, lock.**

```bash
bash ~/secureboot-setup/sb-phase3-enroll.sh --dry-run
sudo bash ~/secureboot-setup/sb-phase3-enroll.sh
```

It refuses to run unless the firmware is in Setup Mode. The lines to expect, in order: `Enrolled keys to the EFI variables!`; `Updated: /boot/limine.conf` and `Config file BLAKE2B successfully enrolled.` and `✓ Signed /boot/EFI/limine/limine_x64.efi` after adding Windows; `Limine EFI update completed successfully.`; the initramfs build for `linux-cachyos` with `Signing /boot/vmlinuz-linux-cachyos`; then the verification block: both Limine copies `signed:`, `fallback: identical to Limine`, the `/Windows 11` entry with `path: boot():/EFI/Microsoft/Boot/bootmgfw.efi`, the menu order (`/+CachyOS` first, `/Windows 11` second), `none, good` for hashes, and `Phase 3 done and verified.`

Expected and harmless: `sbctl verify` lists `/boot/<machine-id>/limine_history/vmlinuz_sha256_...` as "not signed". Limine loads those old kernel copies by hash, and `sbctl` simply reports every unsigned file on the ESP. Immediately after enrollment `sbctl status` can still say `Setup Mode: Enabled` (the flag refreshes after a reboot on this firmware); the key databases themselves can be read back with the snippet in B1.

**B6. Pre-flight check before switching Secure Boot on.**

```bash
sudo bash ~/secureboot-setup/sb-verify.sh
```

Proceed only on `All checks passed.` On any `PROBLEM`, do not enable Secure Boot; the usual fix is `sudo limine-enroll-config`, then re-run.

**B7. Firmware: switch Secure Boot on.** Reboot into the firmware setup and enable Secure Boot, keeping the keys just enrolled. Decline any offer to load factory or default keys. If the firmware refuses to activate Secure Boot, or still reports Setup Mode with a key present, stop and do not clear the keys again.

**B8. Confirm.**

```bash
sbctl status
```

```text
Installed:    ✓ sbctl is installed
Setup Mode:   ✓ Disabled
Secure Boot:  ✓ Enabled
Vendor Keys:  microsoft
```

Then boot the `CachyOS` entry, reboot, boot the `Windows 11` entry, and in Windows run `msinfo32` and look for `Secure Boot State: On`.

### Part C: clean up

```bash
rm -rf -- ~/Downloads/win11-iso ~/Downloads/win11-stage
sudo pacman -Rns wimlib
```

`wimlib` is only needed to split a Windows image; removal is optional (nothing depends on it). **Keep** `~/secureboot-setup/`, `/root/secureboot-backup/` and the off-disk copy of the signing keys. The stick itself still holds the Windows 11 installer.

## 6. Final state achieved

| Item | State |
|---|---|
| Secure Boot | Enabled; `SetupMode=0`; `Vendor Keys: microsoft` |
| `PK` | 1 certificate: `Platform Key` (new, sbctl) |
| `KEK` | 3: `Key Exchange Key`; `Microsoft Corporation KEK CA 2011`; `Microsoft Corporation KEK 2K CA 2023` |
| `db` | 6: `Database Key`; `Microsoft Corporation UEFI CA 2011`; `Microsoft Windows Production PCA 2011`; `Microsoft Option ROM UEFI CA 2023`; `Microsoft UEFI CA 2023`; `Windows UEFI CA 2023` |
| Bootloader | Limine, signed, `limine.conf` checksum enrolled; fallback `BOOTX64.EFI` identical to it |
| Limine menu | `/+CachyOS` first (default), `/Windows 11` second (EFI chainload of `bootmgfw.efi`) |
| UEFI boot order | `Limine`, `Windows Boot Manager`, `UEFI OS` (fallback path) |
| `/etc/default/limine` | Adds `ENABLE_ENROLL_LIMINE_CONFIG="yes"`; `FIND_BOOTLOADERS="no"` unchanged |
| Hooks | `/etc/boot/hooks/post.d/95-sync-limine-fallback` keeps the fallback in sync |
| Windows | Windows 11 Pro, build 26300.9457, on the same NVMe, same EFI partition |
| Temporary files | ISO and staging tree deleted; `wimlib` removed |

### What was verified, and how

- **Read directly from the firmware and `sbctl`:** `SecureBoot=1`, `SetupMode=0`, `sbctl status` shows Secure Boot enabled with `Vendor Keys: microsoft`; `PK`, `KEK` and `db` contents read back after enrollment as listed above; UEFI boot entries intact.
- **From the phase 3 run output:** keys enrolled, config checksum enrolled, both Limine copies signed and identical, `Windows 11` entry present with CachyOS first, no path without a hash.
- **Reported by the owner:** the Windows install from the stick succeeded, and both systems work with Secure Boot on.
- **Not captured in this record:** the output of `flash-win11-usb.sh` on the real stick, the output of `sb-verify.sh` on the real ESP, and the Windows `msinfo32` reading.

## 7. Maintenance and recovery

**Day to day**

- After **any** hand edit of `/boot/limine.conf`, run `sudo limine-enroll-config`, then `sudo bash ~/secureboot-setup/sb-verify.sh`. An edit without re-enrolling makes Limine panic under Secure Boot.
- Kernel and initramfs updates need nothing extra: the hooks regenerate hashes, re-enroll the checksum and re-sign Limine, and `95-sync-limine-fallback` re-copies the fallback.

**If something does not boot**

- Switch Secure Boot **off** in the firmware: the machine then boots as before (Limine treats Secure Boot as inactive when the firmware variable is off). The firmware's own `Windows Boot Manager` entry also remains.
- Restore the config saved by phase 3: copy the right file from `/root/secureboot-backup/limine.conf.pre-phase3-<timestamp>` over `/boot/limine.conf`, then `sudo limine-enroll-config`. Phase 1 also saved a full copy of the ESP as `esp-<timestamp>.tar.zst`, taken before any change.

**Keys**

- Keep an off-disk copy of `/var/lib/sbctl` (the tarball from phase 1). Losing the keys is how the firmware ended up holding keys nobody could sign with, and the cure is the whole Setup Mode flow again.

**Windows notes**

- The Windows partition was plain NTFS, not BitLocker, when the keys were changed. If BitLocker or Device Encryption is turned on later, do not change Secure Boot keys again, or Windows will ask for the recovery key.
- With your own Platform Key, Windows cannot apply Microsoft's later Secure Boot certificate updates by itself, so Windows Security may show a certificate warning. The 2023 certificates are already enrolled, so booting is unaffected.

## 8. Gotchas met along the way

- **Microsoft's API rejects scripts** (`SentinelReject`). Use the browser route; do not try to evade the check.
- **Scripts in `/tmp` disappear at reboot.** Phase 3 had to be recreated after the BIOS visit. Keep them in `~/secureboot-setup/`.
- **Shell aliases mangle output.** `ls` and `du` are aliased to `eza` and `dust` here; use `/usr/bin/ls` and `/usr/bin/du` when parsing.
- **The `limine-entry-tool` wrapper escalates with `sudo` by itself**, even for `--help`. Read usage from the real binary instead: `/usr/lib/limine/limine-entry-tool --help`.
- **`/boot` is root-only** (`fmask=0077`), so `limine.conf` cannot be read without `sudo`.
- **`sbctl status` can show a stale `Setup Mode: Enabled`** right after a successful enrollment; reboot, then re-check.
- **`FIND_BOOTLOADERS=yes` does not find Windows.** Add it with `limine-entry-tool --add-efi`.
- **`sbctl verify` is not a Windows check.** It reports Microsoft-signed files as unsigned (they are signed by Microsoft, not by your key).
- **Do not use the BIOS "restore factory keys"** in this flow; clear the keys instead.

## Appendix: the scripts

Save each as its name in `~/secureboot-setup/`. Differences from the versions as run: `flash-win11-usb.sh` has a serial placeholder (the real value was this stick's serial) and a generic erase warning; `sb-phase1-prepare.sh` has a generic closing sentence. `sb-phase3-enroll.sh` and `sb-verify.sh` are exactly as run.

<details>
<summary><code>flash-win11-usb.sh</code> (Part A, step A7)</summary>

```bash
#!/usr/bin/env bash
# Write an already-extracted Windows 11 ISO tree onto a pendrive (UEFI, GPT + FAT32).
#
#   sudo bash flash-win11-usb.sh <stage_dir>            # real run (asks for confirmation)
#   bash     flash-win11-usb.sh --dry-run <stage_dir>   # guards + printed plan, changes nothing
#
# <stage_dir> is the ISO contents with install.wim already split into install*.swm
# (FAT32 cannot hold a file >= 4 GiB).
set -euo pipefail

# ID_SERIAL_SHORT of the pendrive to flash:
#   udevadm info --query=property --name=/dev/sdX | grep ID_SERIAL_SHORT
EXPECT_SERIAL="REPLACE_WITH_ID_SERIAL_SHORT"
LABEL="WIN11"

DRY=0
if [[ "${1:-}" == "--dry-run" ]]; then DRY=1; shift; fi
STAGE="${1:?usage: $0 [--dry-run] <stage_dir>}"

say()  { printf '\n==> %s\n' "$*"; }
die()  { printf 'ABORT: %s\n' "$*" >&2; exit 1; }
run()  { if (( DRY )); then printf 'WOULD RUN: %s\n' "$*"; else "$@"; fi; }

(( DRY )) || [[ $EUID -eq 0 ]] || die "run as root: sudo bash $0 $STAGE"

# 1. Stage tree must look like a bootable Windows install tree.
say "Checking stage tree: $STAGE"
for f in bootmgr efi/boot/bootx64.efi sources/boot.wim sources/setup.exe; do
  [[ -f "$STAGE/$f" ]] || die "stage tree is missing $f"
done
[[ -f "$STAGE/sources/install.swm" || -f "$STAGE/sources/install.wim" ]] \
  || die "stage tree has no sources/install.swm or install.wim"
big=$(find "$STAGE" -type f -size +4294967294c | head -1)
[[ -z "$big" ]] || die "file too large for FAT32: $big (split install.wim first)"
need=$(du -sb "$STAGE" | cut -f1)
printf 'stage size: %s bytes\n' "$need"

# 2. Resolve the pendrive by serial number, never by a remembered /dev/sdX letter.
say "Locating pendrive by serial $EXPECT_SERIAL"
DEV=""
for d in /sys/block/sd*; do
  [[ -e "$d/removable" && "$(<"$d/removable")" == 1 ]] || continue
  props=$(udevadm info --query=property --name="/dev/${d##*/}")
  if grep -qx "ID_SERIAL_SHORT=$EXPECT_SERIAL" <<<"$props" && grep -qx "ID_BUS=usb" <<<"$props"; then
    [[ -z "$DEV" ]] || die "more than one device matches serial $EXPECT_SERIAL"
    DEV="/dev/${d##*/}"
  fi
done
[[ -n "$DEV" ]] || die "pendrive with serial $EXPECT_SERIAL not found (unplugged?)"
size=$(( $(<"/sys/block/${DEV##*/}/size") * 512 ))
(( size >= need + 64*1024*1024 )) || die "$DEV ($size bytes) is too small for the stage tree"

# 3. Never touch anything backing the running system.
mapfile -t mounts < <(lsblk -nro MOUNTPOINTS "$DEV" | tr ' ' '\n' | sed '/^$/d')
for m in "${mounts[@]}"; do
  case "$m" in
    /|/boot*|/home*|/var*|/usr*|/etc*|/srv*|/root*) die "$DEV has a partition mounted at $m" ;;
  esac
done

say "Target"
lsblk -o NAME,SIZE,TRAN,RM,FSTYPE,LABEL,MODEL,MOUNTPOINTS "$DEV"
echo
echo "Everything on $DEV will be ERASED."
if (( DRY )); then
  echo "(dry run: no confirmation asked, nothing will be changed)"
else
  read -r -p "Type  ERASE $EXPECT_SERIAL  to continue: " answer
  [[ "$answer" == "ERASE $EXPECT_SERIAL" ]] || die "confirmation did not match"
fi

MNT=$(mktemp -d /mnt/win11-usb.XXXXXX 2>/dev/null || mktemp -d)
cleanup() { mountpoint -q "$MNT" 2>/dev/null && umount "$MNT" || true; rmdir "$MNT" 2>/dev/null || true; }
trap cleanup EXIT

say "Unmounting, wiping and partitioning $DEV (GPT, one FAT32 partition)"
while read -r p mp; do [[ -z "$mp" ]] || run umount "$p"; done < <(lsblk -nro PATH,MOUNTPOINT "$DEV")
run wipefs -a "$DEV"
run dd if=/dev/zero of="$DEV" bs=1M count=16 conv=fsync status=none
run parted -s "$DEV" mklabel gpt mkpart "$LABEL" fat32 1MiB 100% set 1 msftdata on
run partprobe "$DEV"
run udevadm settle
PART="${DEV}1"
if (( ! DRY )); then
  for _ in $(seq 1 20); do [[ -b "$PART" ]] && break; sleep 0.5; done
  [[ -b "$PART" ]] || die "partition $PART did not appear"
fi
run mkfs.vfat -F 32 -n "$LABEL" "$PART"

say "Copying Windows files"
run mount "$PART" "$MNT"
run cp -r --no-preserve=all "$STAGE"/. "$MNT"/
run sync
run umount "$MNT"

say "Verifying: re-reading the pendrive from the device, not from cache"
if (( DRY )); then
  echo "WOULD RUN: drop caches, mount read-only, diff -rq $STAGE <mount>"
else
  echo 3 > /proc/sys/vm/drop_caches
  mount -o ro "$PART" "$MNT"
  if diff -rq "$STAGE" "$MNT"; then
    echo "VERIFY OK: every file on the pendrive matches the stage tree."
  else
    die "VERIFY FAILED: pendrive contents differ from the stage tree"
  fi
  umount "$MNT"
  sync
fi

say "Done. $DEV is a UEFI-bootable Windows 11 installer (label $LABEL)."
```

</details>

<details>
<summary><code>sb-phase1-prepare.sh</code> (Part B, step B2)</summary>

```bash
#!/usr/bin/env bash
# Secure Boot, phase 1 of 3: prepare. Safe to re-run.
#   sudo bash sb-phase1-prepare.sh
# Installs sbctl, backs up the ESP + Limine settings + new signing keys, and prints the
# current Limine/ESP state. Does NOT touch firmware variables, the bootloader, or limine.conf.
set -euo pipefail

[[ $EUID -eq 0 ]] || { echo "run as root: sudo bash $0" >&2; exit 1; }

TS=$(date +%Y%m%d-%H%M%S)
BK=/root/secureboot-backup
say() { printf '\n==> %s\n' "$*"; }

say "1/4 Install sbctl"
pacman -S --needed --noconfirm sbctl

say "2/4 Back up the ESP and Limine settings -> $BK"
install -d -m 700 "$BK"
tar --zstd -C /boot -cpf "$BK/esp-$TS.tar.zst" .
cp -a /etc/default/limine "$BK/default-limine-$TS"

say "3/4 Create signing keys (private keys stay in /var/lib/sbctl)"
if [[ -f /var/lib/sbctl/keys/PK/PK.key ]]; then
  echo "keys already exist, leaving them alone"
else
  sbctl create-keys
fi
tar --zstd -C /var/lib -cpf "$BK/sbctl-keys-$TS.tar.zst" sbctl
chmod 600 "$BK"/sbctl-keys-*.tar.zst
ls -l "$BK"
sbctl status || true

say "4/4 Current Limine / ESP state (read-only)"
found=0
for f in /boot/limine.conf /boot/limine/limine.conf /boot/EFI/limine/limine.conf /boot/EFI/BOOT/limine.conf /boot/boot/limine.conf; do
  if [[ -f $f ]]; then
    found=1
    echo "----- $f ($(wc -l <"$f") lines; first 120 shown) -----"
    head -n 120 "$f"
  fi
done
(( found )) || echo "no limine.conf found in the usual places"

echo "----- ESP files -----"
find /boot -maxdepth 4 -type f -printf '%9s  %p\n' | sort -k2 | head -80
df -h /boot | tail -1

echo "----- binary identity -----"
limine --version 2>&1 | head -1
sha256sum /usr/share/limine/BOOTX64.EFI /boot/EFI/limine/limine_x64.efi /boot/EFI/BOOT/BOOTX64.EFI \
          /boot/EFI/Microsoft/Boot/bootmgfw.efi 2>&1 | sed 's/^/  /'

cat <<EOF

Phase 1 done. Nothing about how you boot has changed.
Keys + ESP backups are in $BK -- copy sbctl-keys-*.tar.zst somewhere safe and OFF this disk.
If the firmware already holds keys you cannot sign with, the next step is a BIOS reset to Setup Mode.
EOF
```

</details>

<details>
<summary><code>sb-phase3-enroll.sh</code> (Part B, step B5)</summary>

```bash
#!/usr/bin/env bash
# Secure Boot, phase 3 of 3: enroll keys, list Windows in Limine, sign Limine + lock its config.
#   sudo bash sb-phase3-enroll.sh             # real run (only when firmware is in Setup Mode)
#   bash     sb-phase3-enroll.sh --dry-run    # prints the plan, changes nothing
#
# Result: Limine (and its UEFI fallback copy) signed with your sbctl key, the limine.conf checksum
# enrolled into it, Microsoft's certificates enrolled so the firmware accepts Windows' boot manager,
# and a "Windows 11" entry in the Limine menu. Secure Boot itself is switched on afterwards in the BIOS.
set -euo pipefail

DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

ESP=/boot
CONF=$ESP/limine.conf
LIMINE_EFI=$ESP/EFI/limine/limine_x64.efi
FALLBACK=$ESP/EFI/BOOT/BOOTX64.EFI
WINBM=$ESP/EFI/Microsoft/Boot/bootmgfw.efi
DEFAULTS=/etc/default/limine
HOOK=/etc/boot/hooks/post.d/95-sync-limine-fallback
BK=/root/secureboot-backup
GLOBAL_GUID=8be4df61-93ca-11d2-aa0d-00e098032b8c

say() { printf '\n==> %s\n' "$*"; }
die() { printf 'ABORT: %s\n' "$*" >&2; exit 1; }
run() { if (( DRY )); then printf 'WOULD RUN: %s\n' "$*"; else "$@"; fi; }
efivar_byte() { od -An -tu1 -j4 -N1 "/sys/firmware/efi/efivars/$1-$GLOBAL_GUID" 2>/dev/null | tr -d ' ' || true; }

(( DRY )) || [[ $EUID -eq 0 ]] || die "run as root: sudo bash $0"

say "Preflight (nothing is changed until every check passes)"
[[ -d /sys/firmware/efi ]]                  || die "not booted in UEFI mode"
command -v sbctl >/dev/null                 || die "sbctl is missing (run phase 1)"
[[ -f /var/lib/sbctl/keys/PK/PK.key ]] || (( DRY )) || die "no sbctl keys (run phase 1)"
SETUP=$(efivar_byte SetupMode); SB=$(efivar_byte SecureBoot)
echo "SetupMode=${SETUP:-?}  SecureBoot=${SB:-?}"
if (( ! DRY )); then
  [[ $SETUP == 1 ]] || die "firmware is not in Setup Mode. Do the BIOS key-clear step first (not 'restore factory keys')."
  [[ $SB == 0 ]]    || die "Secure Boot is already active"
  for f in "$LIMINE_EFI" "$FALLBACK" "$WINBM" "$CONF" "$DEFAULTS"; do [[ -f $f ]] || die "missing $f"; done
  # Limine uses the first config it finds; the enrolled checksum must belong to that one.
  others=$(find "$ESP" -iname limine.conf ! -path "$CONF" 2>/dev/null || true)
  [[ -z $others ]] || die "extra limine.conf copies would break the enrolled checksum, remove them first:"$'\n'"$others"
fi

if (( ! DRY )); then
  install -d -m 700 "$BK"
  TS=$(date +%Y%m%d-%H%M%S)
  cp -a "$CONF"     "$BK/limine.conf.pre-phase3-$TS"
  cp -a "$DEFAULTS" "$BK/default-limine.pre-phase3-$TS"
  echo "config backups in $BK"
fi

say "1/5 Enroll your keys + Microsoft's keys into the firmware"
run sbctl enroll-keys --microsoft

say "2/5 Turn on Limine config-checksum enrollment"
if grep -qE '^ENABLE_ENROLL_LIMINE_CONFIG=' "$DEFAULTS" 2>/dev/null; then
  run sed -i 's/^ENABLE_ENROLL_LIMINE_CONFIG=.*/ENABLE_ENROLL_LIMINE_CONFIG="yes"/' "$DEFAULTS"
else
  (( DRY )) && echo "WOULD APPEND to $DEFAULTS: ENABLE_ENROLL_LIMINE_CONFIG=\"yes\"" \
            || printf '\nENABLE_ENROLL_LIMINE_CONFIG="yes"\n' >> "$DEFAULTS"
fi

say "3/5 List Windows in the Limine menu (chainload through the firmware, which checks Microsoft's signature)"
if (( ! DRY )) && grep -qi 'bootmgfw.efi' "$CONF"; then
  echo "Windows entry already present, leaving it"
else
  run limine-entry-tool --add-efi "Windows 11" "$WINBM" --comment "Windows Boot Manager"
fi

say "4/5 Regenerate boot files: hashes for kernel+initramfs, enroll config checksum, sign Limine"
run limine-update

say "5/5 Keep the UEFI fallback loader identical to the signed Limine (and keep it that way on updates)"
if (( DRY )); then
  echo "WOULD INSTALL hook $HOOK and copy $LIMINE_EFI -> $FALLBACK"
else
  install -d "$(dirname "$HOOK")"
  cat > "$HOOK" <<'EOF'
#!/usr/bin/env bash
# Keep the UEFI fallback loader identical to the signed, config-enrolled Limine binary.
src=/boot/EFI/limine/limine_x64.efi
dst=/boot/EFI/BOOT/BOOTX64.EFI
[[ -f $src && -f $dst ]] || exit 0
cmp -s "$src" "$dst" && exit 0
cp -f "$src" "$dst" && sync -f "$dst"
EOF
  chmod 755 "$HOOK"
  "$HOOK"
fi

say "Verification"
if (( DRY )); then
  echo "WOULD CHECK: Windows entry in $CONF, kernel paths carry hashes, Limine + fallback signed and identical"
  echo; echo "Dry run complete. Nothing was changed."; exit 0
fi

fail=0
echo "--- sbctl status ---"; sbctl status || true
echo "--- signature check (our key; Microsoft-signed Windows files are expected to show as unsigned here) ---"
VER=$(sbctl verify 2>&1 || true)
grep -iE 'limine|BOOTX64' <<<"$VER" || true
for f in "$LIMINE_EFI" "$FALLBACK"; do
  line=$(grep -F "$f" <<<"$VER" || true)
  if [[ $line == *"✓"* ]]; then echo "signed:   $f"; else echo "NOT SIGNED: $f"; fail=1; fi
done
cmp -s "$LIMINE_EFI" "$FALLBACK" && echo "fallback: identical to Limine" || { echo "fallback differs from Limine"; fail=1; }

echo "--- Windows entry ---"
grep -qi 'bootmgfw.efi' "$CONF" && grep -niE '^/[^/]|bootmgfw' "$CONF" || { echo "Windows entry missing from $CONF"; fail=1; }

echo "--- top-level menu order (first one is the default) ---"
grep -nE '^/[^/+]|^/\+' "$CONF" || true

echo "--- paths without a BLAKE2b hash (Limine would panic under Secure Boot) ---"
bad=$(grep -nE '^[[:space:]]*(path|kernel_path|module_path|dtb_path):' "$CONF" \
        | grep -viE '\.efi' | grep -vE '#[0-9a-f]{128}' || true)
if [[ -n $bad ]]; then echo "$bad"; fail=1; else echo "none, good"; fi

if (( fail )); then
  cat <<EOF

PROBLEMS FOUND above. Do NOT enable Secure Boot yet.
Config backups: $BK   (restore with: cp -a $BK/limine.conf.pre-phase3-* $CONF && limine-enroll-config)
EOF
  exit 1
fi

cat <<EOF

Phase 3 done and verified. Reboot into the BIOS and switch Secure Boot ON (keep the keys you just enrolled;
decline any prompt to load factory/default keys). Then boot Limine and try both entries.

Recovery if anything goes wrong: BIOS -> Secure Boot OFF boots exactly as before.
After this, any manual edit of $CONF must be followed by:  sudo limine-enroll-config
EOF
```

</details>

<details>
<summary><code>sb-verify.sh</code> (Part B, step B6)</summary>

```bash
#!/usr/bin/env bash
# Read-only pre-flight for Secure Boot + Limine. Run it before switching Secure Boot on.
#   sudo bash sb-verify.sh
# Checks:
#   [1] the checksum baked into both Limine binaries equals the current limine.conf
#   [2] every kernel/initramfs hash written in limine.conf matches the file on the ESP
#   [3] Limine and its fallback copy are signed with your sbctl key
#   [4] firmware key state (informational)
# Under Secure Boot a mismatch in [1] or [2] makes Limine panic at boot, so any PROBLEM here
# means: do not enable Secure Boot yet.
set -uo pipefail

ESP=${ESP:-/boot}
CONF=$ESP/limine.conf
BINS=("$ESP/EFI/limine/limine_x64.efi" "$ESP/EFI/BOOT/BOOTX64.EFI")
GUID=8be4df61-93ca-11d2-aa0d-00e098032b8c
fail=0
ok()  { printf '  ok       %s\n' "$*"; }
bad() { printf '  PROBLEM  %s\n' "$*"; fail=1; }

[[ -f $CONF ]] || { echo "cannot read $CONF (run with sudo; /boot is root-only)"; exit 2; }

echo "[1] config checksum enrolled in each Limine binary"
H=$(b2sum "$CONF" | cut -d' ' -f1)
for b in "${BINS[@]}"; do
  if [[ -f $b ]] && grep -aqF "$H" "$b"; then ok "$b"; else bad "$b lacks the current limine.conf checksum"; fi
done

echo "[2] file hashes referenced by limine.conf"
re='^[[:space:]]*(path|kernel_path|module_path|dtb_path):[[:space:]]*\$?boot\(\):/(.+)#([0-9a-f]{128})[[:space:]]*$'
n=0; m=0
while IFS= read -r line; do
  [[ $line =~ $re ]] || continue
  rel=${BASH_REMATCH[2]}; want=${BASH_REMATCH[3]}; f=$ESP/$rel; n=$((n + 1))
  if [[ ! -f $f ]]; then bad "missing   $rel"; m=$((m + 1)); continue; fi
  got=$(b2sum "$f" | cut -d' ' -f1)
  if [[ $got != "$want" ]]; then bad "MISMATCH  $rel"; m=$((m + 1)); fi
done < "$CONF"
if (( n == 0 )); then bad "no hashed paths found in $CONF"
elif (( m == 0 )); then ok "$n hashed paths all match their files"; fi

echo "[3] signatures (your key)"
if [[ $ESP == /boot ]] && command -v sbctl >/dev/null; then
  V=$(sbctl verify 2>&1 || true)
  for b in "${BINS[@]}"; do
    l=$(grep -F "$b" <<<"$V" || true)
    if [[ $l == *"✓"* ]]; then ok "signed $b"; else bad "not signed: $b"; fi
  done
else
  echo "  (skipped)"
fi

echo "[4] firmware state (informational)"
pk=no; ls /sys/firmware/efi/efivars/ 2>/dev/null | grep -q '^PK-' && pk=yes
byte() { od -An -tu1 -j4 -N1 "/sys/firmware/efi/efivars/$1-$GUID" 2>/dev/null | tr -d ' '; }
echo "  Platform Key enrolled: $pk   SetupMode=$(byte SetupMode)   SecureBoot=$(byte SecureBoot)"

echo
if (( fail )); then
  echo "PROBLEMS FOUND: do NOT enable Secure Boot yet."
  echo "Usual fix:  sudo limine-enroll-config   (then re-run this)"
  exit 1
fi
echo "All checks passed."
```

</details>
