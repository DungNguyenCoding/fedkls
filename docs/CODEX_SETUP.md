# FedKLS Codex setup and fresh-window startup

**Purpose:** give each new Codex IDE/CLI conversation the current *workflow* and *task contract* without importing previous chat history. See `WORKFLOW.md` (roles, permissions and experiment lifecycle), `PROJECT_STATUS.md` (dated status) and `TASK_TEMPLATE.md` (specific input/output contract). Existing `AGENTS.md` is automatically read by Codex when applicable; keep it concise.

## 1. Which files are read, in which order?

A **new window** should:

1. Read `AGENTS.md` and `docs/WORKFLOW.md` (persistent rules).
2. Read `docs/PROJECT_STATUS.md`, then independently verify `git status`, branch, HEAD and newer reports; status is dated, not automatically live.
3. Read `docs/ARCHITECTURE.md`, `docs/ALGORITHMS.md`, `docs/WIRELESS.md` and `docs/EXPERIMENTS.md` as relevant; `docs/REPRODUCIBILITY.md` for experimental or resume work.
4. Read the **exact approved task specification** under `docs/tasks/` (if provided). If no task is approved, inspect only, summarize and stop.
5. For finished runs, use `reports/README.md` and the strict evidence, not historical prose or unverified checkpoints.

### Ready-to-paste new conversation prompt

> We are continuing the FedKLS research repository in a new Codex conversation. Read `AGENTS.md`, `docs/WORKFLOW.md`, `docs/PROJECT_STATUS.md` and `docs/CODEX_SETUP.md`. Check the actual Git branch/HEAD/working tree, Python interpreter and the imported `bayesfl` path. For the approved task I provide, read its exact `docs/tasks/TASK-*.md` brief and only the necessary scientific docs. The researcher and ChatGPT design scientific changes; implement only the approved scope. Do not start or resume training, push, rewrite historical evidence or alter scientific algorithms without explicit approval. First summarize the task's **purpose, inputs, outputs, tests and approval gates**, then execute only if the task is approved. If this is onboarding only, stop after the summary.

## 2. What does `config.toml` actually control?

Codex supports a user configuration at **`~/.codex/config.toml`**, trusted project overrides at **`<repo>/.codex/config.toml`**, and separate named profiles in **`~/.codex/<profile-name>.config.toml`** (CLI `--profile name`). The IDE and CLI share the settings layers; the IDE model picker may override the configured model. A project must be trusted before its `.codex` overrides load. Settings are not automatic task-classification rules.

**Our committed project file** `.codex/config.toml` contains only safe defaults: `approval_policy="on-request"` and `sandbox_mode="workspace-write"`. It intentionally **does not set a model or reasoning effort** because project-local settings take precedence over user profile settings. These controls are guardrails, **not a substitute for the explicit prohibition on unapproved GPU runs in `WORKFLOW.md`**. Higher-priority user/IDE/organization policies may override or restrict them.

**Manual choice of reasoning/model:** choose via the IDE selector for each new conversation, or use named profiles in the CLI. Codex cannot infer `PREPARE_RUN` and silently switch to a cheap model from this TOML alone.

| Task | Suggested selection | Why |
| --- | --- | --- |
| Read docs, routine test execution, log triage, report extraction | GPT-6.1 Sol **Medium** (`fedkls-routine`) | Clear, bounded verification; reduce context/usage |
| Implement an approved algorithm change, write numerical tests, diagnose integration failure | GPT-6.1 Sol **High** (`fedkls-implementation`) | Careful code and interface reasoning |
| Verify hard math invariants, cross-check two algorithm paths, investigate subtle checkpoint/race errors | GPT-6.1 Sol **Extra High** (`fedkls-critical-review`) | Higher-depth verification of a difficult problem |

All included profiles use the same model ID to minimize availability surprises and vary **reasoning effort**. Models available in the Codex IDE may differ across accounts; if GPT-6.1 Sol isn't selectable, use an available model from the selector and keep the task/verification contracts unchanged. If a cheaper model such as Luna or a stronger model such as Astra is offered, it may be chosen manually **after** checking availability and evaluating results; this is not a guaranteed capability of the included profiles.

## 3. Installing optional user profiles (once, manually)

The files in `docs/codex-profiles/` are **examples**. They are not read automatically from that folder. On the SSH machine where Codex actually runs, review your existing `~/.codex` configuration, then optionally install profile copies without replacing existing files:

```bash
cd /home/micl/DungNDH/fedkls
mkdir -p "$HOME/.codex"
ls -la "$HOME/.codex/config.toml" 2>/dev/null || true
cp -n docs/codex-profiles/fedkls-*.config.toml "$HOME/.codex/"
```

The optional `user-default.example.toml` is a **merge reference**, not a command to overwrite your `~/.codex/config.toml`. Existing authentication, MCP and model settings should be preserved. In VS Code, open **Codex Settings → Open config.toml** to inspect user defaults. In the CLI, for example:

```bash
cd /home/micl/DungNDH/fedkls
codex --profile fedkls-routine
codex --profile fedkls-implementation
codex --profile fedkls-critical-review
```

`--profile` is a CLI selector; do not assume the IDE automatically exposes these profile names. For IDE tasks, manually choose the corresponding model and effort in the available UI; the actual setting shown in the UI is authoritative.

### Practical caveats

- Configuration precedence: CLI overrides > trusted project `.codex/config.toml` > selected user profile > base user config > system/builtin defaults. Do not place model settings in project config if you want task-profile switching.
- Modern named profiles are **separate `.config.toml` files**, not `[profiles.*]` sections in `.codex/config.toml`.
- Do not use `approval_policy="never"` or `sandbox_mode="danger-full-access"` as an attempt to make tests faster. For host CUDA/Ray execution, deliberately approve a separate bounded test and note whether it runs inside a sandbox or on the host.
- Do not store secrets, SSH keys or API tokens in versioned `.codex/` configuration or task briefs.
- Validate a configuration locally with the installed Codex version. The examples are syntax-tested as TOML, not runtime-tested on this SSH machine.

Official reference: [Codex config basics](https://learn.chatgpt.com/docs/config-file/config-basic), [config reference](https://learn.chatgpt.com/docs/config-file/config-reference), and [advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced).

## 4. Keeping many Codex windows consistent

Before closing a task/window, write durable *facts*, not chain-of-thought: exact commit and changed files, commands run with exit codes, tests and skips, saved run IDs, report paths, remaining issues and next approval boundary. For a substantive task, update its `docs/tasks/TASK-...md` status and `docs/PROJECT_STATUS.md` after checking the evidence. New windows should not read every legacy archived document. If task context is already in a report, link to the report rather than copying it into `AGENTS.md`.

**Researcher's policy for long GPU runs:** Codex prepares and tests scripts/commands; the **researcher manually runs** `LAUNCH`, uses `MONITOR`, and later executes `EXTRACT RESULTS`. Codex must not keep a session open to wait for a multi-hour `nohup` job. See `WORKFLOW.md`.
