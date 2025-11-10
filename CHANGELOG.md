# Changelog

All notable changes to Bardic will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added core dataclass models in `core/models.py`: ObjectType, ChartLocation, ChartDateTime, CelestialPosition, HouseCusps, Aspect, CalculatedChart
- Added 4 tests for core dataclass models
- Added Protocol definitions: EphemerisEngine, HouseSystemEngine, AspectEngine, OrbEngine, DignityCalculator, ChartComponent
- Added configuration models: AspectConfig, CalculationConfig
- Added SwissEphemerisEngine and MockEphemerisEngine and 2 tests

### Removed

### Changed

- Complete restructuring of the package to composable design.
- Pivoted on houses: Chart supports multiple house systems, data models updated

### Fixed

## [0.1.0]

- Initial version of `starlight`
