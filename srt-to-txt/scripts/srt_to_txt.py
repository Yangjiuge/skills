#!/usr/bin/env python3
"""Convert local SRT subtitle files into TXT while keeping cue time ranges, removing numeric indices, and deleting duplicated inline timestamps after speaker labels."""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_EXTENSIONS = {".srt"}
DEFAULT_ENCODING_CANDIDATES = ("utf-8-sig", "utf-8", "utf-16", "gb18030", "latin-1")
TIMECODE_RANGE_RE = re.compile(
    r"^\s*\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}(?:\s+.+)?\s*$"
)
INLINE_PREFIX_TIMECODE_RE = re.compile(
    r"^(?P<prefix>.{1,60}?\S)\s+\d{2}:\d{2}:\d{2}[,.]\d{3}(?P<body>\S.*)$"
)
TAG_RE = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class ConversionTask:
    src: Path
    dst: Path


@dataclass(frozen=True)
class ConversionFailure:
    src: Path
    dst: Path
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a local .srt subtitle file or a directory tree of .srt files "
            "into .txt files that keep cue time ranges, remove numeric indices, "
            "and delete duplicated inline timestamps inside dialogue lines."
        )
    )
    parser.add_argument("--input-path", type=Path, required=True, help="Source .srt file or source directory.")
    parser.add_argument("--output-path", type=Path, required=True, help="Destination .txt file path or destination directory.")
    parser.add_argument(
        "--strip-tags",
        action="store_true",
        help="Remove inline HTML-style subtitle tags such as <i> or <font>.",
    )
    parser.add_argument(
        "--encoding",
        default=None,
        help="Force a specific input encoding instead of using the built-in fallback list.",
    )
    parser.add_argument(
        "--extra-extension",
        action="append",
        default=[],
        help="Additional file extension to include during directory scans.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Replace existing output .txt files.")
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="In directory mode, continue processing other files when one file fails and print a summary at the end.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the planned conversions without writing files.")
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of files to process.")
    return parser.parse_args()


def normalize_extension(value: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        raise ValueError("empty extension")
    if not normalized.startswith("."):
        normalized = f".{normalized}"
    return normalized


def validate_args(args: argparse.Namespace) -> None:
    if not args.input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {args.input_path}")
    if args.limit is not None and args.limit < 0:
        raise ValueError("--limit must be 0 or greater")
    for extension in args.extra_extension:
        normalize_extension(extension)


def collect_extensions(extra_extensions: list[str]) -> set[str]:
    extensions = set(DEFAULT_EXTENSIONS)
    for extension in extra_extensions:
        extensions.add(normalize_extension(extension))
    return extensions


def collect_sources(input_path: Path, extensions: set[str], limit: int | None) -> list[Path]:
    if input_path.is_file():
        if limit == 0:
            return []
        return [input_path]

    sources = sorted(
        path
        for path in input_path.rglob("*")
        if path.is_file() and path.suffix.lower() in extensions
    )
    if limit is not None:
        return sources[:limit]
    return sources


def resolve_single_output(src: Path, output_path: Path) -> Path:
    if output_path.exists():
        if output_path.is_dir():
            return output_path / f"{src.stem}.txt"
        if output_path.suffix.lower() != ".txt":
            raise ValueError("Single-file output paths must end with .txt.")
        return output_path

    if output_path.suffix:
        if output_path.suffix.lower() != ".txt":
            raise ValueError("Single-file output paths must end with .txt.")
        return output_path

    return output_path / f"{src.stem}.txt"


def build_tasks(input_path: Path, output_path: Path, extensions: set[str], limit: int | None) -> list[ConversionTask]:
    sources = collect_sources(input_path, extensions, limit)
    if input_path.is_file():
        if not sources:
            return []
        return [ConversionTask(src=sources[0], dst=resolve_single_output(sources[0], output_path))]

    tasks: list[ConversionTask] = []
    for src in sources:
        relative = src.relative_to(input_path).with_suffix(".txt")
        tasks.append(ConversionTask(src=src, dst=output_path / relative))
    return tasks


def read_text_with_fallback(path: Path, forced_encoding: str | None) -> str:
    encodings = (forced_encoding,) if forced_encoding else DEFAULT_ENCODING_CANDIDATES
    last_error: UnicodeError | None = None
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeError as exc:
            last_error = exc
    message = (
        f"Could not decode {path} with forced encoding '{forced_encoding}'"
        if forced_encoding
        else f"Could not decode {path} with fallback encodings: {', '.join(encodings)}"
    )
    raise RuntimeError(message) from last_error


def strip_inline_prefix_timecode(line: str) -> str:
    match = INLINE_PREFIX_TIMECODE_RE.match(line)
    if not match:
        return line
    return f"{match.group('prefix')} {match.group('body')}".strip()


def clean_text_line(line: str, *, strip_tags: bool) -> str:
    cleaned = html.unescape(line.rstrip())
    if strip_tags:
        cleaned = TAG_RE.sub("", cleaned)
    cleaned = strip_inline_prefix_timecode(cleaned)
    return cleaned


def convert_block(block: str, *, strip_tags: bool) -> str:
    lines = block.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ""

    if lines[0].strip().isdigit():
        lines.pop(0)
    if not lines:
        return ""

    output_lines: list[str] = []
    if TIMECODE_RANGE_RE.match(lines[0]):
        output_lines.append(lines[0].strip())
        lines = lines[1:]

    for line in lines:
        output_lines.append(clean_text_line(line, strip_tags=strip_tags))

    while output_lines and not output_lines[-1].strip():
        output_lines.pop()
    return "\n".join(output_lines).strip()


def convert_srt_text(raw_text: str, *, strip_tags: bool) -> str:
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    blocks = [block for block in re.split(r"\n\s*\n", normalized) if block.strip()]
    converted_blocks = [convert_block(block, strip_tags=strip_tags) for block in blocks]
    converted_blocks = [block for block in converted_blocks if block]
    return ("\n\n".join(converted_blocks).rstrip() + "\n") if converted_blocks else ""


def ensure_output_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def convert_file(task: ConversionTask, args: argparse.Namespace) -> int:
    if task.dst.exists() and not args.overwrite:
        print(f"SKIP exists: {task.dst}", file=sys.stderr)
        return 0

    print(f"{task.src} -> {task.dst}")
    if args.dry_run:
        return 0

    raw_text = read_text_with_fallback(task.src, args.encoding)
    output_text = convert_srt_text(raw_text, strip_tags=args.strip_tags)
    ensure_output_parent(task.dst)
    task.dst.write_text(output_text, encoding="utf-8", newline="\n")
    return 0


def print_failure_summary(failures: list[ConversionFailure]) -> None:
    if not failures:
        return
    print("", file=sys.stderr)
    print(f"Completed with {len(failures)} failed file(s):", file=sys.stderr)
    for failure in failures:
        print(f"- {failure.src} -> {failure.dst}", file=sys.stderr)
        print(f"  {failure.message}", file=sys.stderr)


def main() -> int:
    args = parse_args()
    try:
        validate_args(args)
        tasks = build_tasks(
            input_path=args.input_path,
            output_path=args.output_path,
            extensions=collect_extensions(args.extra_extension),
            limit=args.limit,
        )
        if not tasks:
            print("No matching input files found.", file=sys.stderr)
            return 1
        failures: list[ConversionFailure] = []
        for task in tasks:
            if args.continue_on_error and args.input_path.is_dir():
                try:
                    convert_file(task, args)
                except Exception as exc:
                    failures.append(
                        ConversionFailure(
                            src=task.src,
                            dst=task.dst,
                            message=str(exc),
                        )
                    )
                    print(f"ERROR {task.src}: {exc}", file=sys.stderr)
            else:
                convert_file(task, args)
        if failures:
            print_failure_summary(failures)
            return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
