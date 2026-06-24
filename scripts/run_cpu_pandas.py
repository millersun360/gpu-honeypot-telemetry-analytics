#!/usr/bin/env python3
"""
CPU baseline analytics for synthetic Cowrie telemetry.

Reads Cowrie-style JSONL with pandas, computes brute-force analytics on CPU,
and records benchmark timing for comparison with the GPU path.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass
class BenchmarkTiming:
    parse_ms: float
    analysis_ms: float
    total_ms: float
    records_per_second: float


def positive_int(value: str) -> int:
    try:
        parsed = int(value.replace("_", ""))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc

    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")

    return parsed


def optional_path(value: str | None) -> Path | None:
    if value is None or value == "":
        return None
    return Path(value)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run CPU/Pandas baseline analytics on Cowrie JSONL telemetry.")
    parser.add_argument("--input", required=True, help="Cowrie-style JSONL input file.")
    parser.add_argument("--bucket-minutes", type=positive_int, default=5, help="Time bucket size in minutes.")
    parser.add_argument("--min-attempts", type=positive_int, default=100, help="Minimum attempts for suspicious IPs.")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional markdown summary output path. If omitted, no markdown file is written.",
    )
    parser.add_argument(
        "--benchmark-csv",
        default="results/benchmark_results.csv",
        help="Benchmark CSV path. Default: results/benchmark_results.csv.",
    )
    parser.add_argument(
        "--top-n",
        type=positive_int,
        default=20,
        help="Number of rows to show for top-value summaries. Default: 20.",
    )
    return parser


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def series_or_empty(df: pd.DataFrame, column: str) -> pd.Series:
    if column in df.columns:
        return df[column]
    return pd.Series([""] * len(df), index=df.index, dtype="string")


def read_and_normalize(input_path: Path, bucket_minutes: int) -> tuple[pd.DataFrame, float]:
    started = time.perf_counter()
    df = pd.read_json(input_path, lines=True)

    if "timestamp" not in df.columns:
        raise ValueError("Input file does not contain a timestamp column")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["username"] = series_or_empty(df, "username").fillna("").astype(str)
    df["password"] = series_or_empty(df, "password").fillna("").astype(str)
    df["src_ip"] = series_or_empty(df, "src_ip").fillna("").astype(str)
    df["eventid"] = series_or_empty(df, "eventid").fillna("").astype(str)
    df["protocol"] = series_or_empty(df, "protocol").fillna("").astype(str)
    df["dst_port"] = pd.to_numeric(series_or_empty(df, "dst_port"), errors="coerce").astype("Int64")
    df["src_port"] = pd.to_numeric(series_or_empty(df, "src_port"), errors="coerce").astype("Int64")
    df["time_bucket"] = df["timestamp"].dt.floor(f"{bucket_minutes}min")
    df["credential_pair"] = df["username"] + ":" + df["password"]
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    return df, elapsed_ms


def top_counts(series: pd.Series, top_n: int) -> pd.Series:
    return series.value_counts().head(top_n)


def format_counts_series(series: pd.Series, title: str, top_n: int) -> list[str]:
    lines = [f"### {title}"]
    if series.empty:
        lines.append("")
        lines.append("_No data._")
        return lines

    lines.append("")
    lines.append("| Value | Count |")
    lines.append("| --- | ---: |")
    for value, count in series.head(top_n).items():
        lines.append(f"| `{value}` | {int(count):,} |")
    return lines


def format_data_frame(df: pd.DataFrame, title: str, columns: Iterable[str], top_n: int) -> list[str]:
    lines = [f"### {title}"]
    if df.empty:
        lines.append("")
        lines.append("_No data._")
        return lines

    lines.append("")
    header = list(columns)
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join("---" if col == header[0] else "---:" for col in header) + " |")
    for _, row in df.head(top_n).iterrows():
        values = []
        for col in header:
            cell = row[col]
            if isinstance(cell, (int, float)) and col != header[0]:
                values.append(f"{int(cell):,}")
            else:
                values.append(f"`{cell}`" if col == header[0] else str(int(cell)) if pd.notna(cell) else "")
        lines.append("| " + " | ".join(values) + " |")
    return lines


def build_summary(df: pd.DataFrame, bucket_minutes: int, min_attempts: int, top_n: int) -> dict[str, object]:
    event_counts = df["eventid"].value_counts()
    top_usernames = df["username"].value_counts().head(top_n)
    top_passwords = df["password"].value_counts().head(top_n)
    top_src_ips = df["src_ip"].value_counts().head(top_n)
    top_pairs = df["credential_pair"].value_counts().head(top_n)
    bucket_counts = df["time_bucket"].value_counts().sort_index()

    per_ip = (
        df.groupby("src_ip")
        .agg(
            attempts=("src_ip", "size"),
            unique_usernames=("username", "nunique"),
            unique_passwords=("password", "nunique"),
        )
        .sort_values(["attempts", "unique_usernames", "unique_passwords"], ascending=[False, False, False])
    )
    suspicious = per_ip[per_ip["attempts"] >= min_attempts]

    return {
        "event_counts": event_counts,
        "top_usernames": top_usernames,
        "top_passwords": top_passwords,
        "top_src_ips": top_src_ips,
        "top_pairs": top_pairs,
        "bucket_counts": bucket_counts,
        "per_ip": per_ip,
        "suspicious": suspicious,
    }


def print_console_summary(df: pd.DataFrame, summary: dict[str, object], top_n: int, min_attempts: int) -> None:
    event_counts = summary["event_counts"]
    top_usernames = summary["top_usernames"]
    top_passwords = summary["top_passwords"]
    top_src_ips = summary["top_src_ips"]
    top_pairs = summary["top_pairs"]
    bucket_counts = summary["bucket_counts"]
    per_ip = summary["per_ip"]
    suspicious = summary["suspicious"]

    print("CPU baseline summary")
    print(f"records: {len(df):,}")
    print("event IDs:")
    for key, value in event_counts.items():
        print(f"  {key}: {value:,}")
    print(f"time buckets ({bucket_counts.index.min()} -> {bucket_counts.index.max()})")
    print(bucket_counts.head(top_n).to_string())
    print("top usernames:")
    print(top_usernames.to_string())
    print("top passwords:")
    print(top_passwords.to_string())
    print("top source IPs:")
    print(top_src_ips.to_string())
    print("top credential pairs:")
    print(top_pairs.to_string())
    print("suspicious high-volume source IPs:")
    if suspicious.empty:
        print(f"  none found at threshold >= {min_attempts}")
    else:
        print(suspicious.head(top_n).to_string())
    print("per-source-IP aggregates (top 10):")
    print(per_ip.head(10).to_string())


def build_markdown_report(
    input_path: Path,
    df: pd.DataFrame,
    summary: dict[str, object],
    timing: BenchmarkTiming,
    bucket_minutes: int,
    min_attempts: int,
    benchmark_row: dict[str, object],
) -> str:
    event_counts = summary["event_counts"]
    top_usernames = summary["top_usernames"]
    top_passwords = summary["top_passwords"]
    top_src_ips = summary["top_src_ips"]
    top_pairs = summary["top_pairs"]
    bucket_counts = summary["bucket_counts"]
    per_ip = summary["per_ip"]
    suspicious = summary["suspicious"]

    lines: list[str] = []
    lines.append("# CPU Pandas Baseline Summary")
    lines.append("")
    lines.append(f"- Input: `{input_path}`")
    lines.append(f"- Records: `{len(df):,}`")
    lines.append(f"- Bucket minutes: `{bucket_minutes}`")
    lines.append(f"- Minimum attempts: `{min_attempts}`")
    lines.append(f"- Parse/load time: `{timing.parse_ms:.2f} ms`")
    lines.append(f"- Analysis time: `{timing.analysis_ms:.2f} ms`")
    lines.append(f"- Total time: `{timing.total_ms:.2f} ms`")
    lines.append(f"- Records per second: `{timing.records_per_second:,.2f}`")
    lines.append("")
    lines.append("## Event IDs")
    lines.append("")
    lines.append("| Event ID | Count |")
    lines.append("| --- | ---: |")
    for key, value in event_counts.items():
        lines.append(f"| `{key}` | {int(value):,} |")
    lines.append("")
    lines.extend(format_counts_series(top_usernames, "Top Usernames", len(top_usernames)))
    lines.append("")
    lines.extend(format_counts_series(top_passwords, "Top Passwords", len(top_passwords)))
    lines.append("")
    lines.extend(format_counts_series(top_src_ips, "Top Source IPs", len(top_src_ips)))
    lines.append("")
    lines.extend(format_counts_series(top_pairs, "Top Credential Pairs", len(top_pairs)))
    lines.append("")
    lines.append("## Attempts Per Time Bucket")
    lines.append("")
    lines.append(f"Bucket size: `{bucket_minutes}` minutes")
    lines.append("")
    lines.append("| Time Bucket | Attempts |")
    lines.append("| --- | ---: |")
    for ts, count in bucket_counts.items():
        lines.append(f"| `{ts}` | {int(count):,} |")
    lines.append("")
    lines.append("## Per-Source-IP Aggregates")
    lines.append("")
    lines.append("| Source IP | Attempts | Unique Usernames | Unique Passwords |")
    lines.append("| --- | ---: | ---: | ---: |")
    for src_ip, row in per_ip.head(20).iterrows():
        lines.append(
            f"| `{src_ip}` | {int(row['attempts']):,} | {int(row['unique_usernames']):,} | {int(row['unique_passwords']):,} |"
        )
    lines.append("")
    lines.append("## Suspicious High-Volume Source IPs")
    lines.append("")
    lines.append(f"Threshold: `{min_attempts}` attempts")
    lines.append("")
    if suspicious.empty:
        lines.append("_None found._")
    else:
        lines.append("| Source IP | Attempts | Unique Usernames | Unique Passwords |")
        lines.append("| --- | ---: | ---: | ---: |")
        for src_ip, row in suspicious.head(20).iterrows():
            lines.append(
                f"| `{src_ip}` | {int(row['attempts']):,} | {int(row['unique_usernames']):,} | {int(row['unique_passwords']):,} |"
            )

    lines.append("")
    lines.append("## Benchmark Row")
    lines.append("")
    lines.append("| records | method | input_file | file_size_mb | parse_ms | analysis_ms | total_ms | records_per_second | notes |")
    lines.append("| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |")
    lines.append(
        f"| {benchmark_row['records']:,} | {benchmark_row['method']} | `{benchmark_row['input_file']}` | "
        f"{benchmark_row['file_size_mb']:.2f} | {benchmark_row['parse_ms']:.2f} | {benchmark_row['analysis_ms']:.2f} | "
        f"{benchmark_row['total_ms']:.2f} | {benchmark_row['records_per_second']:,.2f} | {benchmark_row['notes']} |"
    )
    return "\n".join(lines) + "\n"


def append_benchmark_csv(csv_path: Path, row: dict[str, object]) -> None:
    ensure_parent_dir(csv_path)
    fieldnames = [
        "records",
        "method",
        "input_file",
        "file_size_mb",
        "parse_ms",
        "analysis_ms",
        "total_ms",
        "records_per_second",
        "notes",
    ]
    file_exists = csv_path.exists() and csv_path.stat().st_size > 0
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({name: row[name] for name in fieldnames})


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        parser.error(f"input file not found: {input_path}")

    output_path = optional_path(args.output)
    benchmark_csv = Path(args.benchmark_csv)
    file_size_mb = input_path.stat().st_size / (1024 * 1024)

    total_started = time.perf_counter()
    parse_started = time.perf_counter()
    try:
        df, parse_ms = read_and_normalize(input_path, args.bucket_minutes)
    except Exception as exc:
        parser.exit(2, f"run_cpu_pandas: {exc}\n")
    parse_ms = (time.perf_counter() - parse_started) * 1000.0

    analysis_started = time.perf_counter()
    summary = build_summary(df, args.bucket_minutes, args.min_attempts, args.top_n)
    analysis_ms = (time.perf_counter() - analysis_started) * 1000.0
    total_ms = (time.perf_counter() - total_started) * 1000.0
    records_per_second = len(df) / (total_ms / 1000.0) if total_ms > 0 else 0.0
    timing = BenchmarkTiming(
        parse_ms=parse_ms,
        analysis_ms=analysis_ms,
        total_ms=total_ms,
        records_per_second=records_per_second,
    )

    benchmark_row = {
        "records": int(len(df)),
        "method": "cpu_pandas",
        "input_file": str(input_path),
        "file_size_mb": float(file_size_mb),
        "parse_ms": float(parse_ms),
        "analysis_ms": float(analysis_ms),
        "total_ms": float(total_ms),
        "records_per_second": float(records_per_second),
        "notes": f"bucket_minutes={args.bucket_minutes}; min_attempts={args.min_attempts}",
    }

    print_console_summary(df, summary, args.top_n, args.min_attempts)
    print("")
    print("Benchmark timing")
    print(f"  parse/load: {parse_ms:.2f} ms")
    print(f"  analysis: {analysis_ms:.2f} ms")
    print(f"  total: {total_ms:.2f} ms")
    print(f"  file size: {file_size_mb:.2f} MB")
    print(f"  records/sec: {records_per_second:,.2f}")

    append_benchmark_csv(benchmark_csv, benchmark_row)

    if output_path is not None:
        ensure_parent_dir(output_path)
        markdown = build_markdown_report(
            input_path=input_path,
            df=df,
            summary=summary,
            timing=timing,
            bucket_minutes=args.bucket_minutes,
            min_attempts=args.min_attempts,
            benchmark_row=benchmark_row,
        )
        output_path.write_text(markdown, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
