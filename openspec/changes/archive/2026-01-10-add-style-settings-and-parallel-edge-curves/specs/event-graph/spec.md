## ADDED Requirements

### Requirement: Display and appearance settings
The system SHALL provide a single settings UI that allows configuring date/time display and appearance parameters.

#### Scenario: Configure date display and appearance together
- **WHEN** the user opens the settings UI
- **THEN** the system SHALL allow changing the date display mode
- **AND THEN** the system SHALL allow changing node size and edge thickness

#### Scenario: Settings apply immediately
- **GIVEN** the user changes one or more settings
- **WHEN** the user confirms the settings UI
- **THEN** the canvas SHALL update to reflect the new settings without restarting

### Requirement: Parallel directed edges are visually distinct
The system SHALL render multiple identical directed edges between the same source and target using curved paths to avoid overlap.

#### Scenario: Two edges between same nodes
- **GIVEN** there are two directed edges A->B
- **WHEN** the user views the canvas
- **THEN** the two edges SHALL be rendered with visibly different curved paths

#### Scenario: Curved edges remain interactive
- **GIVEN** there are two directed edges A->B
- **WHEN** the user attempts to select or toggle either edge
- **THEN** each edge SHALL remain selectable and its toggle control SHALL remain usable
