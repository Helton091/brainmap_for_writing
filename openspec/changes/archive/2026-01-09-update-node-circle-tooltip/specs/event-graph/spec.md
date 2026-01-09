## ADDED Requirements

### Requirement: Compact node rendering
The system SHALL render each node as a small circle and SHALL hide node body text on the canvas.

#### Scenario: Hide body text
- **WHEN** the node is displayed on the canvas
- **THEN** the node’s body text SHALL NOT be rendered directly on the node

#### Scenario: Display node date label
- **WHEN** the node has an event date
- **THEN** the system SHALL render the date label for the node

#### Scenario: Display placeholder for undated nodes
- **WHEN** the node does not have an event date
- **THEN** the system SHALL render a placeholder label for the node

### Requirement: Hover tooltip shows node text
The system SHALL show the node’s full event text as a tooltip when the cursor hovers over the node.

#### Scenario: Hover shows tooltip
- **WHEN** the user hovers the cursor over a node
- **THEN** the system SHALL display a tooltip containing the node’s event text

### Requirement: User manual
The system SHALL provide a user manual describing node creation, editing, import, connecting, and saving.

#### Scenario: User reads manual
- **WHEN** the user opens the user manual file distributed with the project
- **THEN** the manual SHALL describe the core workflows and shortcuts
