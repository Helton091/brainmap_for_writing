## ADDED Requirements

### Requirement: WASD pan
The system SHALL allow panning the canvas view using WASD keys.

#### Scenario: Pan with keys
- **GIVEN** the canvas has focus
- **WHEN** the user presses W/A/S/D
- **THEN** the viewport SHALL move up/left/down/right accordingly

### Requirement: Stable edge toggle hit area
The system SHALL make the plus/minus control on edges reliably clickable.

#### Scenario: Toggle collapsed state
- **GIVEN** a visible edge with a plus/minus control
- **WHEN** the user clicks the control
- **THEN** the edge collapse state SHALL toggle

### Requirement: Robust TXT import markers
The system SHALL recognize common date marker variants in TXT import.

#### Scenario: Single-digit month/day
- **GIVEN** a marker like `【2200.7.1】`
- **WHEN** the user imports the TXT
- **THEN** the system SHALL parse the marker as a valid date

### Requirement: Merge TXT import
The system SHALL merge imported TXT content into the current project without overwriting existing layout or edges.

#### Scenario: Preserve existing state
- **GIVEN** an existing project with nodes, edges, and manual positions
- **WHEN** the user imports a TXT file
- **THEN** existing node positions and edges SHALL remain unchanged
- **AND THEN** imported nodes SHALL be added and laid out without moving existing nodes
