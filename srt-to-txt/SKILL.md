---
name: srt-to-txt
description: Convert local SRT subtitle files into TXT while keeping each cue time range and dialogue text, removing numeric cue indices, and deleting duplicated inline timestamps that repeat inside dialogue lines after speaker labels. Use when Codex needs to turn one `.srt` file or a directory tree of subtitle files into readable `.txt` files for review, note-taking, summarization, or downstream text processing.
---

# SRT to TXT

## Core Goal
- Convert one local `.srt` file or a directory tree of `.srt` files into `.txt`.
- Keep each cue time range line such as `00:00:00,000 --> 00:00:05,000`.
- Remove numeric cue index lines such as `1`, `2`, `3`.
- Remove duplicated inline timestamps that reappear inside dialogue lines after a short leading label, such as `∑¢—‘»À 1  00:00:00,960...`.
- Preserve speaker labels and dialogue content.
- Write UTF-8 `.txt` output.

## Required Script
- Use `scripts/srt_to_txt.py`.
- Rely only on Python standard library modules.
- Default to non-destructive behavior unless the user explicitly wants overwrites.
- Use `--continue-on-error` for directory batches when one bad file should not stop the full run.

## Quick Start
1. Convert one subtitle file into one text file:

```bash
python scripts/srt_to_txt.py \
  --input-path /path/to/video.srt \
  --output-path /path/to/video.txt
```

2. Convert a directory tree and keep matching relative paths:

```bash
python scripts/srt_to_txt.py \
  --input-path /path/to/subtitles \
  --output-path /path/to/text-output
```

3. Preview the conversion plan without writing files:

```bash
python scripts/srt_to_txt.py \
  --input-path /path/to/subtitles \
  --output-path /path/to/text-output \
  --dry-run
```

4. Replace existing `.txt` outputs when rerunning a batch:

```bash
python scripts/srt_to_txt.py \
  --input-path /path/to/subtitles \
  --output-path /path/to/text-output \
  --overwrite
```

5. Continue a directory batch even when one file fails to decode or write:

```bash
python scripts/srt_to_txt.py \
  --input-path /path/to/subtitles \
  --output-path /path/to/text-output \
  --continue-on-error
```

## Default Behavior
- Treat file input as one conversion task.
- Treat directory input as recursive and preserve relative subdirectories in the output tree.
- Preserve blank lines between subtitle cues.
- Keep the main SRT time range line for each cue.
- Remove numeric cue index lines when present.
- Remove duplicated inline timestamps inside dialogue lines, but do not remove the main cue time range line.
- Preserve speaker labels and dialogue text.
- Decode common subtitle encodings with a built-in fallback list and write UTF-8 output.

## Main Arguments
- `--input-path`: source `.srt` file or source directory.
- `--output-path`: output `.txt` file path or output directory.
- `--overwrite`: replace existing output files.
- `--continue-on-error`: in directory mode, keep processing other files and print a failure summary at the end.
- `--dry-run`: print the plan without writing files.
- `--encoding`: force a specific input encoding.
- `--strip-tags`: remove inline subtitle tags.
- `--extra-extension`: include additional suffixes during directory scans.
- `--limit`: cap the number of files processed for a quick check.

## Output Rules
- Output keeps the cue time range line.
- Output removes the numeric cue index line.
- Output keeps speaker labels and dialogue text.
- Output removes duplicated inline timestamps that immediately follow a short leading label.

## Script
- `scripts/srt_to_txt.py`
