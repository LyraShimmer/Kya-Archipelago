# Release and compatibility versions

- **GitHub release name:** `9.0.0-beta1` — an outward-facing beta milestone.
- **Launcher implementation:** `0.9.63` codebase, with its existing matching guards and data compatibility preserved.
- **APWorld implementation:** `0.8.14` — location IDs, world generation logic and version guards retained.

Do **not** replace every occurrence of `0.8.14` or `0.9.63` with `9.0.0`: some literals are compatibility/version checks. Rename the whole protocol only after an explicit review of those checks and a new multiworld test.
