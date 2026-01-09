## ADDED Requirements

### Requirement: Node creation and editing
The system SHALL allow the user to create nodes and edit each node’s event text and optional event date.

#### Scenario: Create a node manually
- **WHEN** the user creates a new node
- **THEN** the system SHALL add a node to the canvas

#### Scenario: Edit node content
- **WHEN** the user edits a node’s event text
- **THEN** the system SHALL persist the updated text in the project data

#### Scenario: Set or clear node date
- **WHEN** the user sets or clears a node’s event date
- **THEN** the system SHALL persist the updated date state in the project data

### Requirement: Import nodes from txt
The system SHALL import nodes from a txt file using the project’s log format.

#### Scenario: Parse dated blocks
- **WHEN** the importer encounters a line formatted as `【YYYY.MM.DD】`
- **THEN** the system SHALL start a new dated node using that date

#### Scenario: Collect block body
- **WHEN** lines follow a dated marker until the next dated marker or end-of-file
- **THEN** the system SHALL store those lines as the node’s event text

#### Scenario: Create undated nodes
- **WHEN** text exists outside any dated marker block
- **THEN** the system SHALL create one or more undated nodes from that text

#### Scenario: Report import errors
- **WHEN** the txt content cannot be parsed according to the expected rules
- **THEN** the system SHALL report a clear error message
- **AND THEN** the system SHALL fail the import operation without creating partial nodes

### Requirement: Default time-based layout
The system SHALL assign an initial layout that places later-dated nodes as far right as practical.

#### Scenario: Layout by date ordering
- **WHEN** the system generates an initial layout for nodes that have dates
- **THEN** nodes with later dates SHALL be placed with greater x-coordinates than earlier dates

#### Scenario: User layout overrides
- **WHEN** the user drags a node to a new position
- **THEN** the system SHALL preserve the user-assigned coordinates on save and reload

### Requirement: Directed relationships between nodes
The system SHALL allow the user to create and remove directed edges between nodes to represent precedence or other logical relationships.

#### Scenario: Create a directed edge
- **WHEN** the user connects a source node to a target node
- **THEN** the system SHALL create a directed edge from source to target

#### Scenario: Remove a directed edge
- **WHEN** the user deletes an existing edge
- **THEN** the system SHALL remove that edge from the project data

### Requirement: Project persistence
The system SHALL save and load the project, including nodes, edges, and node positions.

#### Scenario: Save a project
- **WHEN** the user saves the project
- **THEN** the system SHALL write nodes, edges, and layout coordinates to disk

#### Scenario: Load a project
- **WHEN** the user loads a previously saved project
- **THEN** the system SHALL restore nodes, edges, and layout coordinates
