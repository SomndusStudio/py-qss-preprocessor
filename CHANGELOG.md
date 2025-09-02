# Changelog

All notable changes to this project are documented in this file.  
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]
- Theme switch helper (CLI flag) to compile a named theme in one command.
- Optional stripping of all comments in output (configurable).
- Mixins and includes (under evaluation, only if they remain predictable).
- CLI Watcher

## [0.2.0] — 2025-09-02
### Added
- **Theming workflow**: place variables in theme files (e.g., `assets/themes/dark-theme.qsspp`, `light-theme.qsspp`) and `@import` common styles at the end.
- **Color functions** in the processor: `lighten(...)`, `darken(...)`, `alpha(...)`.
- **CLI**: `ss-qssppc` (compile-only), with clear exit codes and helpful error messages.
- **Python API**: `compile_qss(path)` for on-the-fly compilation.

### Changed
- **Output hygiene**: remove variable declarations from the final `.qss` and clean up surrounding variable-only lines.
- **Documentation**: professional README with international English, usage examples, and theming guidance.

## [0.1.0] — 2025-09-02
### Added
- Initial preprocessor: variables (`\$var: value;`), `@import`, color functions, and basic compilation pipeline.
- Source layout (`src/`), package metadata, and editable install.
- Minimal CLI and API skeleton.

---

**Notes**
- All files are processed as UTF-8.
- The tool is intentionally minimal: no selector nesting, no mixins, no conditionals/loops (to keep QSS output predictable).

