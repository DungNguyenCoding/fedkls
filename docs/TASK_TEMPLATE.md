# FedKLS task specification template

For a sustained/approved task, save a copy as `docs/tasks/TASK-YYYYMMDD-short-description.md`. Keep the *filled* specification short and specific. Do not treat this template as a current work order. Read `docs/WORKFLOW.md` for authorization and output rules.

```markdown
# TASK-YYYYMMDD: <concise name>

Status: PROPOSED | APPROVED | IMPLEMENTED | VERIFIED | BLOCKED
Task type: INSPECT | IMPLEMENT | VERIFY | PREPARE_RUN | STATUS | EXTRACT
Research owner approval: <who approved and when; or NOT APPROVED>

## Purpose / scientific question
<What problem is being solved? Why this task now?>

## Inputs and source of truth
- Git branch / base commit: <exact revision>
- Existing files / interfaces: <paths>
- Approved design or equations: <explicit spec, cite doc section>
- Dataset, partition, seeds, config, source runs (if relevant): <exact identity>
- Dependencies and environment: <only required facts>

## Authorized changes and immutable boundaries
- Allowed writes: <exact directories/files, or NONE>
- Required behavior: <acceptance-level implementation details>
- Must remain unchanged: <FOLA, KL direction, packet, data, config ... as applicable>
- Explicitly forbidden: <training, pushes, resume, changing old artifacts ...>

## Outputs / deliverables
- Code/config/script: <exact expected paths, if applicable>
- Tests: <paths/commands>
- Evidence/report: <reports/... path and required columns/fields>
- If PREPARE_RUN: provide LAUNCH, MONITOR and EXTRACT RESULTS commands; DO NOT RUN.

## Acceptance criteria
- <Observable pass/fail condition 1>
- <Observable pass/fail condition 2>
- <Strict byte integrity and provenance condition if experiment data involved>
- <Source diff reviewed, unchanged protected files confirmed>

## Stop / approval gates
- <Ambiguous science, missing config, unsupported environment or insufficient resource>
- Do not invent missing settings. Diagnose and return options for approval.

## Verification receipt (fill after work)
- Final Git commit / working tree: <...>
- Commands actually run + exit codes: <...>
- Tests passed / failed / skipped: <...>
- Report path(s) and verified run ID(s): <...>
- Training launched? NO unless separately approved and directly observed.
- Remaining risks / exact next action: <...>
```

A new Codex conversation should open the **approved filled task file**, not perform an exploratory redesign. For small, read-only tasks the same fields may be inline in the first prompt. No one should silently promote a PROPOSED study to APPROVED.
