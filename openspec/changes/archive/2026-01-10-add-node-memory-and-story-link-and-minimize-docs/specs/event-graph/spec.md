## ADDED Requirements

### Requirement: Minimizable project documents
The system SHALL allow minimizing and expanding the system prompt and world document panels.

#### Scenario: Minimize and expand panels
- **GIVEN** the system prompt and world document panels are visible
- **WHEN** the user minimizes either panel
- **THEN** the panel content area SHALL be hidden while keeping an affordance to expand

### Requirement: Node memory block
The system SHALL allow setting a memory block on each node.

#### Scenario: Edit node memory block
- **GIVEN** a node exists
- **WHEN** the user edits the node memory block
- **THEN** the system SHALL persist the updated memory block in the project data

### Requirement: Node story txt link
The system SHALL allow linking each node to an external txt file path without storing its contents.

#### Scenario: Link a story txt file
- **GIVEN** a node exists
- **WHEN** the user links a txt file to the node
- **THEN** the system SHALL persist only the file path in the project data

#### Scenario: Do not store story contents
- **GIVEN** a node is linked to a txt file
- **WHEN** the user saves the project
- **THEN** the project file SHALL NOT embed the txt file contents
