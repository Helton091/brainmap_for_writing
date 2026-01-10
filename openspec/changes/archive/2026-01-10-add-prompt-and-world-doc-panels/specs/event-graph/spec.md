## ADDED Requirements

### Requirement: Fixed project documents
The system SHALL provide two fixed UI panels for project-level documents: a system prompt and a world document.

#### Scenario: Panels are visible and editable
- **WHEN** the user opens the application
- **THEN** the system SHALL display the two document panels in the top-left area
- **AND THEN** the user SHALL be able to edit both contents

#### Scenario: Import document from txt
- **WHEN** the user imports a txt file into one of the document panels
- **THEN** the system SHALL replace that panel’s content with the txt content

#### Scenario: Persist documents with project
- **GIVEN** the user edits either document
- **WHEN** the user saves and later opens the project
- **THEN** both document contents SHALL be restored
