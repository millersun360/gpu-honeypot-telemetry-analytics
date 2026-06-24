# Methodology

This project benchmarks a narrow Cowrie/DShield-style SSH brute-force workload using sanitized local telemetry and synthetic scaled datasets.

## Data Sources

- Sanitized local Cowrie sample for pattern extraction
- Synthetic JSONL datasets for 10K, 100K, 1M, and future 10M record benchmarks

## Benchmark Paths

1. CPU/Pandas baseline
2. RAPIDS/cuDF GPU baseline
3. Future normalized CUDA/C++ kernel path

## What Is Measured

The benchmark separates the work into phases so the runtime picture stays honest:

- JSON parse/load
- normalization
- analysis/aggregation
- host/device transfer, if applicable
- kernel execution, if applicable
- total runtime

## Why Phase Separation Matters

JSONL ingestion can dominate end-to-end runtime. If the benchmark only reports a total number, it is easy to miss whether the GPU is actually helping the analysis step or only shifting where the bottleneck lives.

The project therefore compares both:

- total time
- analysis-only time

That makes it possible to see whether RAPIDS/cuDF or CUDA helps after the data is already in a usable form.

## Output Metrics

The current scripts report:

- record count
- event ID counts
- top usernames
- top passwords
- top source IPs
- top credential pairs
- time buckets
- per-source-IP attempt counts
- per-source-IP unique username count
- per-source-IP unique password count
- suspicious high-volume source IPs

## Interpretation Rules

- CPU and GPU results should be compared on the same input dataset
- synthetic source IPs are benchmark signals, not attribution data
- data normalization matters as much as raw compute throughput
- cuDF or CUDA improvements should be interpreted in the context of I/O and parsing overhead

