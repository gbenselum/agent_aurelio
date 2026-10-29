---
description: Research a car or check its maintenance record
---

Use the `agent_aurelio` skill.

Arguments: $ARGUMENTS

If the arguments start with `research`, run Workflow R in the skill for the car described after
that word. Otherwise treat the arguments as the maintenance question and pick the matching
workflow: PROFILE, STATUS, SYMPTOM, DOCUMENT, BIG JOB, BUDGET, INSPECTION, RECALLS or MAINTAIN.

When you research a car, ask for the engine code before anything else. Never fill a profile field
with a guess.
