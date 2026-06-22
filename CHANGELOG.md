# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Unreleased

### Added
- CHANGELOG.md added. Previous history very sparse.

### Changed
- `soulstruct` updated to 2.4.0.
- API for `Binder` changed for new `soulstruct` (`Firelink` compatibility).
- Defined `BothResHKXBHD.get_both_hkx()` vs. `BothResHKXBHD.get_both_hkx_allow_missing()`.
- Added comment on bizarre `hkpConstraintAtom.alignment` post-2015.
- `BaseANIBND` does not load skeleton if already set on instance.
- `RemoPart` stores a list of standard bone names used as roots, to find world-space boundary.

### Fixed
- Numpy float formatting for mopper input fixed.
- Mopper call uses proper tempfile.

---

## [1.2.2] - 2026-03-30

### Added
- Bundled DLLs/EXEs included in pyproject build.

## [1.2.1] - 2026-03-30

### Added
- bumpversion and `havok/version.py` added.

## [1.2.0] - 2026-03-30

### Added
- First tagged version.
