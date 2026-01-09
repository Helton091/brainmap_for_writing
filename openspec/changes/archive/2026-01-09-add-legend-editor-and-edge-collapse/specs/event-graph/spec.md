## ADDED Requirements

### Requirement: Legend editor
The system SHALL provide a legend editor UI allowing the user to assign a short label to each legend color.

#### Scenario: Edit legend label
- **WHEN** the user edits a legend label for a color
- **THEN** the system SHALL persist the label and display it in the legend UI

### Requirement: Edge-level collapse/expand
The system SHALL allow collapsing and expanding individual edges.

#### Scenario: Collapse one outgoing branch
- **GIVEN** node A has edges A->B and A->C
- **WHEN** the user collapses edge A->B
- **THEN** the path A->B downstream nodes SHALL be hidden
- **AND THEN** the path A->C downstream nodes SHALL remain visible

### Requirement: Plus/minus affordance on edges
The system SHALL render a clear plus/minus control on each edge to indicate collapse/expand.

#### Scenario: Render controls
- **WHEN** an edge is visible on the canvas
- **THEN** the edge SHALL show a minus control when expanded
- **AND THEN** the edge SHALL show a plus control when collapsed

### Requirement: Collapsed edge label
The system SHALL display the target node’s minimal note near the plus control for a collapsed edge.

#### Scenario: Show target note
- **GIVEN** edge A->B is collapsed
- **WHEN** the user views the plus control
- **THEN** the control SHALL display B’s note to aid selection

### Requirement: Persist legend and edge collapse
The system SHALL save and load the legend labels and edge collapse state.

#### Scenario: Save and reload
- **WHEN** the user saves and reloads a project
- **THEN** legend labels and edge collapse states SHALL be restored
