# Versions

What this project runs on, where each version was checked, and what was left alone on purpose. Checked on **<YYYY-MM-DD>**. Where something could not be verified, it says so.

## Runtimes and tooling

| Component | Version | Pinned in | Why this one |
| --- | --- | --- | --- |
| <runtime> | <version> | <file> | <lifecycle source: supported until <date> (<where you looked>)> |

## Where it was actually run

| What | Result |
| --- | --- |
| <suite on each supported runtime> | <passes on each> |

**Not run:** <the full stack, the deploy, live services, other browsers, CI on the host>.

## Application dependencies

| Package | Locked | Declared |
| --- | --- | --- |
| <package> | <version> | <range> |

The declared floors equal the tested versions, so an upgrade cannot resolve to something this pass did not run.

## Deliberately not upgraded

| Package | Latest seen | Why not |
| --- | --- | --- |
| <package> | <version> | <reason: breaking change, peer range, visual baselines, data migration> |

## Known advisories

| Before | After |
| --- | --- |
| <n, by severity> | <n, by severity, and what remains and why> |

## Third-party service model IDs

| Service | Default | Checked against |
| --- | --- | --- |
| <vendor> | <model or API version> | <the vendor page or SDK reference, and what was not exercised> |

## Things to watch

- <deprecation warnings and upcoming removals>
