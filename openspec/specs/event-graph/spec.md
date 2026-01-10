# event-graph Specification

## Purpose
TBD - created by archiving change add-event-node-graph. Update Purpose after archive.
## Requirements
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

### Requirement: Clear arrow direction
The system SHALL render directed edges with a clearly visible arrowhead indicating direction.

#### Scenario: Edge direction is unambiguous
- **WHEN** an edge is displayed on the canvas
- **THEN** the arrowhead SHALL make the source-to-target direction visually obvious

### Requirement: Compact default vertical spacing
The system SHALL generate an initial layout with limited vertical dispersion so that nodes appear roughly aligned.

#### Scenario: Nodes have compact y distribution
- **WHEN** nodes are generated by import and auto layout is applied
- **THEN** the y-coordinates of nodes SHALL fall within a limited band rather than spreading widely

### Requirement: Readable tooltip
The system SHALL display node text in a larger, readable tooltip, and the tooltip box SHALL be approximately square.

#### Scenario: Tooltip uses larger font
- **WHEN** the user hovers a node
- **THEN** the tooltip text SHALL use a larger font than the default UI text

#### Scenario: Tooltip box is compact
- **WHEN** the tooltip is displayed
- **THEN** the tooltip content SHALL be wrapped so the tooltip is not overly wide

### Requirement: Zoomable canvas
The system SHALL allow the user to zoom in and out of the canvas.

#### Scenario: Zoom with input gesture
- **WHEN** the user performs the zoom gesture
- **THEN** the view SHALL zoom in or out while keeping the canvas content usable

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

### Requirement: Application entrypoint import stability
The system SHALL start successfully when executed via `python -m brainmap_for_writing` and when packaged as a standalone executable.

#### Scenario: Run as module
- **WHEN** the user runs `python -m brainmap_for_writing`
- **THEN** the application SHALL start without import errors

#### Scenario: Run as executable
- **WHEN** the user runs the packaged executable
- **THEN** the application SHALL start without import errors

