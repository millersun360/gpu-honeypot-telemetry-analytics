# GPU-Accelerated Analytics for DShield-Style Honeypot Telemetry

_A prototype evaluation of CPU, RAPIDS/cuDF, and CUDA approaches for scalable SSH brute-force analytics using sanitized Cowrie logs and synthetic benchmark data._

## Project Overview

This repository explores whether GPU-accelerated dataframe analytics and custom CUDA kernels can reduce analysis time for large-scale Cowrie/DShield-style SSH brute-force telemetry, while preserving privacy through synthetic, non-attributable benchmark data.

The project is written from the perspective of a field solutions architect evaluating an accelerated computing architecture for a cybersecurity telemetry customer. The hypothetical customer workflow is DShield-style honeypot telemetry analysis. The goal is to determine where NVIDIA software and hardware can accelerate high-volume brute-force analytics and where conventional bottlenecks such as JSON parsing, disk I/O, and data normalization still dominate.

NVIDIA DGX Spark is the target local GPU benchmark platform for the accelerated path.

## Problem Statement

Cowrie-style honeypot logs are easy to collect, but the useful work is still expensive at scale. The project focuses on a narrow and measurable workload:

- ingest JSONL telemetry
- normalize login-attempt fields
- aggregate usernames, passwords, source IPs, credential pairs, and time buckets
- identify high-volume brute-force actors
- compare CPU/Pandas against future RAPIDS/cuDF and custom CUDA paths

The benchmark question is not whether the logs are real threat intelligence. The question is where accelerated computing helps when the workload is dominated by repeated aggregation over large telemetry files.

## Stakeholder / Use Case: DShield-Style Honeypot Telemetry

The customer workflow is DShield-style honeypot telemetry analysis: a local operator wants to summarize SSH credential-attempt traffic from Cowrie logs without exporting raw telemetry elsewhere.

The project treats DShield-style honeypot telemetry as the customer workload and asks whether accelerated computing can improve the analysis path for high-volume SSH brute-force events.

## Solution Architect Framing

This project is written from the perspective of a field solutions architect evaluating an accelerated computing architecture for a cybersecurity telemetry customer. The hypothetical customer workflow is DShield-style honeypot telemetry analysis. The goal is to determine where NVIDIA software and hardware can accelerate high-volume brute-force analytics and where conventional bottlenecks such as JSON parsing, disk I/O, and data normalization still dominate.

That framing matters because the useful comparison is not just "CPU versus GPU." It is also:

- parse/load time versus analysis time
- normalized intermediate data versus raw JSONL
- host-side preprocessing versus device-side aggregation
- dataframe analytics versus custom kernel execution

## Data Privacy and Sanitization Model

The repository uses a sanitized local Cowrie sample as the source of truth for pattern extraction. Real source IPs are never preserved in synthetic output. Synthetic source IPs are generated from private, non-attributable ranges so the benchmark data can model skew and actor cardinality without representing real organizations or public Internet sources.

The synthetic datasets are intended for benchmarking, not attribution. They preserve the fields needed for brute-force aggregation, but they deliberately omit broader honeypot context.

## Synthetic Benchmark Data Generation

Synthetic datasets are generated from `data/real/cowrie_sanitized.jsonl` and written directly to disk as JSONL. The generator preserves realistic frequency patterns for usernames, passwords, event IDs, protocols, ports, source-IP skew, and bursty time windows.

The current benchmark line uses:

- `scripts/generate_synthetic_cowrie.py`
- 10K, 100K, 1M, and future 10M record targets
- deterministic seeds for reproducibility
- `--exclude-values` to keep sensitive or distracting tokens out of generated credentials
- `--src-ip-mode private-diverse` by default so the synthetic addresses stay private but do not collapse into a single lab-like subnet

## CPU Baseline

`scripts/run_cpu_pandas.py` implements the current CPU baseline with Pandas. It reads the JSONL telemetry, normalizes the fields used by the benchmark, and computes:

- record count
- event ID counts
- top usernames
- top passwords
- top source IPs
- top credential pairs
- time-bucket counts
- per-source-IP aggregates
- suspicious high-volume source IPs

This baseline is the reference point for future cuDF and CUDA work.

## GPU Baseline with RAPIDS/cuDF

`scripts/run_gpu_cudf.py` defines the GPU baseline path. It is intended to mirror the CPU analytics as closely as practical while using RAPIDS/cuDF for dataframe operations.

This path is relevant because it measures whether GPU dataframe execution can reduce the analysis portion of the workload once the data is already normalized. It also keeps JSON ingestion and host/device transfer visible so the benchmark does not hide the real cost of moving from raw log files to analytics-ready data.

DGX Spark is the intended local NVIDIA platform for this comparison.

## Custom CUDA Kernel Path

The next step after RAPIDS/cuDF is a custom CUDA/C++ path built around a normalized intermediate representation. That future path is meant to test whether a narrower kernel can outperform generic dataframe aggregation for repeated frequency analysis.

In practical terms, the custom kernel path would focus on the stable primitive in this workload:

- map login attempts to compact fields
- count frequencies
- aggregate by time bucket and source actor
- compare host-side preprocessing against device-side execution

## Current Benchmark Results

Validated synthetic benchmark state:

| Metric | Value |
| --- | ---: |
| Synthetic 1M records | 1,000,000 |
| File size | 204.29 MB |
| `cowrie.login.failed` | 949,943 |
| `cowrie.login.success` | 50,057 |
| Unique source IPs | 49,796 |
| Excluded username/password values generated | 0 |
| Forbidden fields generated | 0 |
| Public/non-private source IPs generated | 0 |

Latest CPU/Pandas 1M benchmark:

| Metric | Value |
| --- | ---: |
| Parse/load time | 10,309.56 ms |
| Analysis time | 2,823.88 ms |
| Total time | 13,133.45 ms |
| Records per second | 76,141.46 |

## Contribution Potential

The intended contribution is a reference prototype and benchmark methodology for evaluating accelerated analytics on DShield-style telemetry. The most practical contribution path is a local analyzer that a DShield/Cowrie user could run against their own logs without uploading raw data anywhere.

This repository is most useful as:

- a reproducible performance benchmark
- a local telemetry summarizer
- a testbed for GPU acceleration choices
- a framing example for contribution-oriented optimization work

## Limitations and Non-Claims

This project is not an official DShield component, does not use unpublished DShield infrastructure, and does not claim to represent the full operational workload of SANS ISC. It is a prototype benchmark using sanitized local Cowrie telemetry and synthetic scaled datasets modeled after Cowrie/DShield-style SSH login events.

This project intentionally narrows the DShield/Cowrie workload to SSH credential-attempt analytics. It does not attempt to reproduce full DShield data fidelity, attribution workflows, command/session analysis, malware collection, HTTP honeypot analysis, firewall log processing, or public-IP threat intelligence.

## Roadmap

1. Validate sanitized local Cowrie schema.
2. Generate safe synthetic DShield-style benchmark datasets.
3. Build CPU/Pandas baseline.
4. Add source-IP mode diversity across private RFC1918 ranges.
5. Build RAPIDS/cuDF GPU baseline.
6. Build normalized intermediate representation for CUDA.
7. Implement custom CUDA/C++ frequency-analysis kernel.
8. Benchmark on DGX Spark.
9. Generate 10M final benchmark dataset.
10. Compare CPU, cuDF, and custom CUDA results.
11. Package local analyzer as potential DShield/Cowrie user contribution.
12. Keep tone professional and honest.
