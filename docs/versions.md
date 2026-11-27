# Release and compatibility versions

## v9.0.2-beta (2026-11-27)

- Launcher only: secure WSS/TLS certificate verification fix contributed by [eNigma (@eBigma)](https://github.com/eBigma) through [PR #1](https://github.com/LyraShimmer/Kya-Archipelago/pull/1).
- APWorld and YAML: unchanged from v9.0.1-beta.
- Location IDs, item placements, progression requirements and game rules: unchanged.
- Internal Archipelago protocol values remain unchanged; they are not interchangeable with GitHub release version numbers.

## v9.0.1-beta (2026-11-15)

- Corrected progression logic, six initial fast travels, Wolfen City/Fortress protection, and rune check behavior.
- 318 checks preserved.

## Compatibility warning

Do not replace internal protocol, Launcher or APWorld version literals merely to match the public release version. Review and test protocol changes separately.
