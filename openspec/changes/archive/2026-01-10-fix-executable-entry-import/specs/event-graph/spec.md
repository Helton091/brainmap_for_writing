## ADDED Requirements

### Requirement: Application entrypoint import stability
The system SHALL start successfully when executed via `python -m brainmap_for_writing` and when packaged as a standalone executable.

#### Scenario: Run as module
- **WHEN** the user runs `python -m brainmap_for_writing`
- **THEN** the application SHALL start without import errors

#### Scenario: Run as executable
- **WHEN** the user runs the packaged executable
- **THEN** the application SHALL start without import errors

