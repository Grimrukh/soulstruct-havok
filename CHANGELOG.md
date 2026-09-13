# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

---

## [1.3.2] - 2026-09-13

### Fixed
- `soulstruct 2.4.3` version corrected (NOT `2.4.5`).
- Changelog version corrected (now in 1.3).

## [1.2.6] - 2026-09-13

### Added
- Added `TRSTransform` unit tests.
- Added `TRSTransform.left_divide()` for proper left division of transforms.
  - `TRSTransform.inverse()` is a one-sided inverse, which is now documented, as rotation and non-uniform scale
  are not commutative. `TRSTransform.left_divide()` is a proper left division that accounts for scale and rotation.

### Changed
- `soulstruct 2.4.5` required (`GameType` enum, `Vector.__eq__` breaking change).

### Fixed
- Fixed `TRSTransform.inverse()` ignoring scale when inverting translation.
- Fixed spline compression block size detection (divide by 255, not 256 - last and first frames have same timestamp).

## [1.2.5] - 2026-09-07

### Changed
- Python 3.13+ required.
- pytest settings added.

### Fixed
- Missing HKX resources included.

## [1.2.4] - 2026-09-06

### Added
- Added Quaternion unit tests.

### Changed
- Updated `scipy` version to `>=1.18.0` (scipy immutable Rotation bug fixed).
- Updated `constrata` version to `>=1.3.3`.

### Fixed
- Fixed some Quaternion bugs.

## [1.2.3] - 2026-09-06

### Added
- CHANGELOG.md added. Previous history very sparse.
- GitHub publish to PyPI workflow added.

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
