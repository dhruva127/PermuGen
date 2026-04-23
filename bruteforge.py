#!/usr/bin/env python3
"""Permutation-based wordlist generator with Unicode support."""

from __future__ import annotations

import argparse
import itertools
import math
import string
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, TextIO


DEFAULT_SYMBOLS = r"""!@#$%^&*()-_=+[]{};:'",.<>/?\|`~"""


@dataclass
class Config:
    charset: str
    min_len: int
    max_len: int
    count: int | None
    start: int
    stdout: bool
    output: Path | None
    split_lines: int | None
    quiet: bool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate permutation-based wordlists from custom characters. "
            "Supports Unicode input and streaming output."
        )
    )
    parser.add_argument("--chars", default="", help="Explicit characters to include.")
    parser.add_argument("--lower", action="store_true", help="Include lowercase a-z.")
    parser.add_argument("--upper", action="store_true", help="Include uppercase A-Z.")
    parser.add_argument("--digits", action="store_true", help="Include digits 0-9.")
    parser.add_argument(
        "--symbols",
        action="store_true",
        help=f"Include symbol preset: {DEFAULT_SYMBOLS}",
    )
    parser.add_argument(
        "--symbol-set",
        default=DEFAULT_SYMBOLS,
        help="Custom symbols used when --symbols is set.",
    )
    parser.add_argument(
        "--min-len",
        type=int,
        default=1,
        help="Minimum length for generated permutations.",
    )
    parser.add_argument(
        "--max-len",
        type=int,
        default=1,
        help="Maximum length for generated permutations.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Maximum number of words to output.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Skip first N generated words before output.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Write generated words to stdout.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write generated words to output file.",
    )
    parser.add_argument(
        "--split-lines",
        type=int,
        default=None,
        help=(
            "When --output is used, split files after this many lines "
            "(e.g. out.txt -> out_0001.txt, out_0002.txt)."
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress final summary stats on stderr.",
    )
    return parser


def unique_preserve_order(chars: str) -> str:
    seen: set[str] = set()
    unique_chars: list[str] = []
    for ch in chars:
        if ch not in seen:
            seen.add(ch)
            unique_chars.append(ch)
    return "".join(unique_chars)


def resolve_charset(args: argparse.Namespace, parser: argparse.ArgumentParser) -> str:
    pieces: list[str] = [args.chars]
    if args.lower:
        pieces.append(string.ascii_lowercase)
    if args.upper:
        pieces.append(string.ascii_uppercase)
    if args.digits:
        pieces.append(string.digits)
    if args.symbols:
        pieces.append(args.symbol_set)

    charset = unique_preserve_order("".join(pieces))
    if not charset:
        parser.error(
            "No characters selected. Use --chars and/or --lower --upper --digits --symbols."
        )
    return charset


def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.min_len < 1 or args.max_len < 1:
        parser.error("--min-len and --max-len must be >= 1.")
    if args.min_len > args.max_len:
        parser.error("--min-len cannot be greater than --max-len.")
    if args.count is not None and args.count <= 0:
        parser.error("--count must be a positive integer.")
    if args.start < 0:
        parser.error("--start must be >= 0.")
    if not args.stdout and args.output is None:
        parser.error("Choose at least one output target: --stdout and/or --output.")
    if args.split_lines is not None and args.split_lines <= 0:
        parser.error("--split-lines must be a positive integer.")
    if args.split_lines is not None and args.output is None:
        parser.error("--split-lines requires --output.")


def count_total_permutations(charset_len: int, min_len: int, max_len: int) -> int:
    total = 0
    for n in range(min_len, max_len + 1):
        if n > charset_len:
            continue
        total += math.perm(charset_len, n)
    return total


def permutation_stream(charset: str, min_len: int, max_len: int) -> Iterator[str]:
    for length in range(min_len, max_len + 1):
        if length > len(charset):
            break
        for tup in itertools.permutations(charset, length):
            yield "".join(tup)


class SplitFileWriter:
    def __init__(self, base_path: Path, split_lines: int | None) -> None:
        self.base_path = base_path
        self.split_lines = split_lines
        self.current_file: TextIO | None = None
        self.current_index = 0
        self.lines_in_current = 0
        self.files_created: list[Path] = []

    def _next_path(self) -> Path:
        if self.split_lines is None:
            return self.base_path
        stem = self.base_path.stem
        suffix = self.base_path.suffix
        return self.base_path.with_name(f"{stem}_{self.current_index:04d}{suffix}")

    def _open_new(self) -> None:
        if self.current_file is not None:
            self.current_file.close()
        if self.split_lines is not None:
            self.current_index += 1
        path = self._next_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.current_file = path.open("w", encoding="utf-8", newline="\n")
        self.lines_in_current = 0
        self.files_created.append(path)

    def write_line(self, line: str) -> None:
        if self.current_file is None:
            self._open_new()
        elif self.split_lines is not None and self.lines_in_current >= self.split_lines:
            self._open_new()
        assert self.current_file is not None
        self.current_file.write(f"{line}\n")
        self.lines_in_current += 1

    def close(self) -> None:
        if self.current_file is not None:
            self.current_file.close()
            self.current_file = None


def emit_words(words: Iterable[str], config: Config) -> tuple[int, list[Path]]:
    written = 0
    file_writer = SplitFileWriter(config.output, config.split_lines) if config.output else None

    try:
        for word in words:
            if config.stdout:
                sys.stdout.write(f"{word}\n")
            if file_writer is not None:
                file_writer.write_line(word)
            written += 1
            if config.count is not None and written >= config.count:
                break
    finally:
        if file_writer is not None:
            file_writer.close()

    files = file_writer.files_created if file_writer is not None else []
    return written, files


def parse_config() -> Config:
    parser = build_parser()
    args = parser.parse_args()
    validate_args(args, parser)
    charset = resolve_charset(args, parser)

    max_unique = len(charset)
    if args.min_len > max_unique:
        parser.error(
            f"min length {args.min_len} exceeds unique charset size {max_unique} for permutations."
        )

    total = count_total_permutations(len(charset), args.min_len, args.max_len)
    if total == 0:
        parser.error("No permutations possible with the given charset and length range.")
    if args.start >= total:
        parser.error(f"--start {args.start} is out of range. Total permutations: {total}.")

    return Config(
        charset=charset,
        min_len=args.min_len,
        max_len=args.max_len,
        count=args.count,
        start=args.start,
        stdout=args.stdout,
        output=args.output,
        split_lines=args.split_lines,
        quiet=args.quiet,
    )


def main() -> int:
    config = parse_config()
    if config.stdout:
        # On Windows terminals, default encodings like cp1252 can fail for Unicode output.
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    words = permutation_stream(config.charset, config.min_len, config.max_len)
    if config.start:
        words = itertools.islice(words, config.start, None)

    written, files = emit_words(words, config)
    if not config.quiet:
        summary = [f"Generated: {written}"]
        if config.stdout:
            summary.append("stdout: yes")
        if files:
            summary.append("files: " + ", ".join(str(p) for p in files))
        elif config.output:
            summary.append("files: none")
        print(" | ".join(summary), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
