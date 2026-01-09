## ADDED Requirements

### Requirement: Node color
The system SHALL allow the user to assign a color to each node and SHALL render the node using that color.

#### Scenario: Set node color
- **WHEN** the user selects a color for a node
- **THEN** the system SHALL update the node color and persist it

#### Scenario: Render node color
- **WHEN** a colored node is displayed on the canvas
- **THEN** the node’s fill color SHALL match the assigned color

### Requirement: Minimal node note
The system SHALL allow the user to set a short note for a node and SHALL render that note on the node.

#### Scenario: Edit node note
- **WHEN** the user edits a node note
- **THEN** the system SHALL persist the note

#### Scenario: Display node note
- **WHEN** a node has a note
- **THEN** the system SHALL display the note on the node in a compact form

### Requirement: Collapse and expand outgoing chain
The system SHALL allow the user to collapse or expand a node to hide or show its downstream reachable nodes via directed edges.

#### Scenario: Collapse hides downstream
- **GIVEN** nodes A, B, C with edges A->B and B->C
- **WHEN** the user collapses node A
- **THEN** only A SHALL remain visible

#### Scenario: Collapse at intermediate node
- **GIVEN** nodes A, B, C with edges A->B and B->C
- **WHEN** the user collapses node B
- **THEN** A and B SHALL remain visible
- **AND THEN** C SHALL be hidden

#### Scenario: Expand restores downstream
- **GIVEN** nodes A, B, C with edges A->B and B->C
- **AND GIVEN** node B is collapsed
- **WHEN** the user expands node B
- **THEN** C SHALL become visible again

#### Scenario: Isolated node collapse has no visible effect
- **GIVEN** a node with no edges
- **WHEN** the user collapses or expands the node
- **THEN** the visible canvas content SHALL remain unchanged

### Requirement: Persist color, note, and collapse state
The system SHALL save and load each node’s color, note, and collapse state.

#### Scenario: Save and reload
- **WHEN** the user saves and reloads a project
- **THEN** node colors, notes, and collapse states SHALL be restored
