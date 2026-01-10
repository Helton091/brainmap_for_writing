## ADDED Requirements

### Requirement: Open linked story txt
The system SHALL allow opening a node’s linked story txt file from within the application.

#### Scenario: Open story file
- **GIVEN** a node is linked to a story txt path
- **WHEN** the user triggers the open-story action
- **THEN** the system SHALL open that txt file using the operating system

### Requirement: Export AI-friendly prompt for a node
The system SHALL allow exporting an AI-friendly prompt based on project documents and node context.

#### Scenario: Export prompt
- **GIVEN** a node exists
- **WHEN** the user triggers export for that node
- **THEN** the system SHALL export a txt containing system prompt and world document
- **AND THEN** the system SHALL include all upstream nodes’ memory blocks
- **AND THEN** the system SHALL include the selected node’s text
