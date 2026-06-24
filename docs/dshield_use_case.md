# DShield-Style Honeypot Telemetry Use Case

This repository treats Cowrie/DShield-style SSH login telemetry as a focused customer workload for accelerated analytics evaluation. The goal is to understand whether NVIDIA software and hardware can reduce time-to-insight for brute-force login summaries while keeping the data local and non-attributable.

The project treats DShield-style honeypot telemetry as the customer workload and asks whether accelerated computing can improve the analysis path for high-volume SSH brute-force events.

## What This Telemetry Means Here

In this project, DShield/Cowrie-style telemetry means JSONL records that describe SSH login attempts and the fields needed to summarize them:

- timestamp
- eventid
- username
- password
- protocol
- source IP
- destination port
- source port

That is enough to answer the core brute-force questions without modeling the entire honeypot ecosystem.

## Why SSH Brute-Force Analytics Matter

SSH brute-force traffic is a good benchmark workload because it is repetitive, high-volume, and easy to aggregate. The same questions appear over and over:

- which usernames are being tried most often
- which passwords dominate
- which credential pairs recur
- which source actors are most active
- how attempts cluster in time

Those are simple analytics, but they become expensive when the dataset grows into the millions of records.

## Customer Problem

The customer problem is not "How do we collect more data?" It is "How do we analyze the telemetry we already have fast enough to matter?"

The prototype addresses:

- local log summarization
- high-volume brute-force aggregation
- repeatable CPU versus GPU benchmarking
- the boundary between raw JSON ingestion and actual analysis

## Solutions Architect Mapping

A solutions architect would map the workflow like this:

- local Cowrie logs or sanitized samples feed the benchmark
- Pandas provides the CPU reference path
- RAPIDS/cuDF provides the GPU dataframe path
- custom CUDA kernels provide a narrower device-side path for frequency analysis
- DGX Spark provides a compact NVIDIA platform for local accelerated evaluation

The architecture question is whether the hot path is better handled by a dataframe engine or by a more specialized CUDA implementation once the data is normalized.

## Why RAPIDS/cuDF and CUDA Are Relevant

RAPIDS/cuDF is relevant because the workload is dataframe-heavy: groupby, value counts, joins, and time-bucket aggregation are all natural dataframe operations.

CUDA is relevant because the workload is also repetitive enough to make a custom kernel plausible. If the benchmark eventually normalizes fields into compact arrays, a specialized frequency-analysis kernel may outperform a general-purpose dataframe pipeline.

## Why DGX Spark Is a Useful Local Benchmark Platform

DGX Spark is useful here because it offers a local NVIDIA accelerated environment for:

- reproducible benchmarking
- quick iteration on GPU data paths
- comparisons against CPU baselines on the same dataset
- smaller-scale prototyping before any larger deployment thinking

That makes it a good fit for a contribution-oriented prototype rather than an operations-heavy production claim.

## Outputs That Matter

The outputs that matter for this use case are the ones that help characterize brute-force activity and compare execution paths:

- top usernames
- top passwords
- top credential pairs
- source-IP attempt counts
- time buckets
- high-volume actors
- CPU versus GPU performance comparisons

Those outputs are enough to show whether acceleration changes the analyst experience in a meaningful way.

