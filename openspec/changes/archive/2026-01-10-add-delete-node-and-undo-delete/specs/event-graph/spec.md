## ADDED Requirements

### Requirement: Node deletion
The system SHALL allow the user to delete one or more selected nodes.

#### Scenario: Delete selected node
- **GIVEN** a node is selected
- **WHEN** the user triggers delete
- **THEN** the system SHALL remove that node from the project data

#### Scenario: Delete node removes connected edges
- **GIVEN** a node has one or more incident edges
- **WHEN** the user deletes that node
- **THEN** the system SHALL also remove all edges whose source or target is that node

### Requirement: Undo delete
The system SHALL allow undoing the most recent delete action using Ctrl+Z.

#### Scenario: Undo edge deletion
- **GIVEN** the user deletes one or more edges
- **WHEN** the user presses Ctrl+Z
- **THEN** the system SHALL restore the deleted edges

#### Scenario: Undo node deletion
- **GIVEN** the user deletes one or more nodes
- **AND GIVEN** the deletion removed incident edges
- **WHEN** the user presses Ctrl+Z
- **THEN** the system SHALL restore the deleted nodes and their removed edges

#### Scenario: Undo preserves identity and layout
- **GIVEN** a node has a specific id and coordinates
- **WHEN** the user deletes the node and then presses Ctrl+Z
- **THEN** the restored node SHALL have the same id and coordinates as before deletion

## MODIFIED Requirements

### Requirement: Directed relationships between nodes
The system SHALL allow the user to create and remove directed edges between nodes to represent precedence or other logical relationships.

#### Scenario: Create a directed edge
- **WHEN** the user connects a source node to a target node
- **THEN** the system SHALL create a directed edge from source to target

#### Scenario: Remove a directed edge
- **WHEN** the user deletes an existing edge
- **THEN** the system SHALL remove that edge from the project data
