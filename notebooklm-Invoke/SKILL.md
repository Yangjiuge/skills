---
name: notebooklm
description: NotebookLM CLI wrapper via `python3 {baseDir}/scripts/notebooklm.py` (backed by notebooklm-py). Use for auth, notebooks, chat, sources, notes, sharing, research, and artifact generation/download.
---

# NotebookLM CLI Wrapper (Python)

## Required parameters
- `python3` available.
- `notebooklm-py` installed (CLI binary: `notebooklm`).
- NotebookLM authenticated (`login`).

## Quick start
- Wrapper script: `scripts/notebooklm.py`.
- Command form: `python3 {baseDir}/scripts/notebooklm.py <command> [args...]`.

```bash
python3 {baseDir}/scripts/notebooklm.py login
python3 {baseDir}/scripts/notebooklm.py list
python3 {baseDir}/scripts/notebooklm.py use <notebook_id>
python3 {baseDir}/scripts/notebooklm.py status
python3 {baseDir}/scripts/notebooklm.py ask "Summarize the key takeaways" --notebook <notebook_id>
```

## Output guidance
- Prefer `--json` for machine-readable output where supported.
- Long-running waits are handled by native commands like:
  - `source wait`
  - `artifact wait`
  - `research wait`

## References
- `README.md` (installation, requirements, troubleshooting)
- `references/cli-commands.md`

## Assets
- None.
