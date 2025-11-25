# Construction Robotics Design Brief Generation

## User Request:
{user_prompt}

## Relevant Patent Context:
{context}

## Task:

Generate a comprehensive design brief for the construction robotics system specified in the user request. Use the patent context provided to ground all design choices with citations.

## Requirements:

1. **Overview**: Provide a high-level description of the system, its purpose, and key capabilities.

2. **Modules**: Identify system modules/components with:
   - Name: Module name
   - Function: What the module does
   - Citations: Patent citations supporting this module design

3. **Actuation**: Specify actuation subsystems with:
   - Subsystem: Name of actuation subsystem
   - Choice: Specific actuation mechanism (e.g., electric servo, pneumatic, hydraulic)
   - Why: Rationale for this choice
   - Citations: Patent citations supporting this choice

4. **Sensing**: Specify sensing subsystems with:
   - Subsystem: Name of sensing subsystem
   - Sensors: List of sensors used
   - Why: Rationale for sensor selection
   - Citations: Patent citations supporting this choice

5. **Control**: Specify control architecture with:
   - Layer: Control layer name (e.g., motion control, safety control)
   - Approach: Control approach (e.g., PID, model predictive control)
   - Teleop_or_auto: Teleoperated or autonomous
   - Citations: Patent citations supporting this choice

6. **Materials**: Specify material choices with:
   - Part: Component name
   - Material: Material selection
   - Why: Rationale for material choice
   - Citations: Patent citations supporting this choice

7. **Safety**: Identify safety considerations with:
   - Risk: Safety risk identified
   - Mitigation: Safety mitigation strategy
   - Citations: Patent citations supporting this mitigation

8. **Procedure**: Provide step-by-step implementation procedure as a list of strings.

9. **BOM**: Provide bill of materials with:
   - Item: Component name
   - Qty: Quantity
   - Est_cost_usd: Estimated cost in USD
   - Citations: Patent citations supporting this component

10. **Citations**: Provide full citation list with:
    - patent_number: Patent number (e.g., "US12345678")
    - title: Patent title
    - url: Patent URL
    - reason: Why this patent is relevant

## Citation Format:

- Use format: `(US<patent_number>, section)` for citations
- Use format: `(US<patent_number>, section, claim_1)` for claim-specific citations
- Use `SPECULATIVE` if no patent evidence exists for a design choice

## Important:

- Every design choice MUST have at least one citation or be marked as SPECULATIVE
- Ensure all JSON is valid and properly formatted
- Base all design choices on the patent context provided
- If patent context is insufficient, mark relevant sections as SPECULATIVE

Generate the design brief now:



