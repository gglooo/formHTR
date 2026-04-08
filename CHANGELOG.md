# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.1 - 2026-04-08

### Changed

- fix numpy newer versions handling [#83](https://github.com/grp-bork/formHTR/issues/83)

## 0.1.0 - 2026-04-08

- Packaged project for PyPI with `pyproject.toml`, `src/` layout, and `formhtr` console entry point.
- Introduced a unified CLI with subcommands:
  - `process-logsheet`
  - `manual-align`
  - `select-rois`
  - `annotate-rois`
  - `doctor`
- Added API modules under `formhtr` to support both CLI and programmatic usage.
- Added runtime system dependency checks for `qpdf` and `zbar`, with platform-specific install hints.
- Updated README with installation guidance, system requirements, and a quickstart example.
