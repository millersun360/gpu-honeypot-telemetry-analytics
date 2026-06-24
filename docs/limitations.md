# Limitations

This project is intentionally narrow. It is designed to evaluate accelerated analytics on Cowrie/DShield-style SSH brute-force telemetry, not to claim broad operational coverage.

## Non-Claims

- Not an official DShield component
- Not production validated
- Not a SANS endorsed artifact
- Not a real attacker attribution dataset
- Not a substitute for operational DShield tooling

## Data Fidelity Limits

- Synthetic source IPs are non-attributable and not real public IPs
- The dataset does not model command or session behavior
- The dataset does not model malware collection behavior
- The dataset does not include HTTP honeypot telemetry
- The dataset does not include firewall telemetry
- The dataset does not cover the full DShield operational workflow

## Performance Interpretation Limits

- CPU and GPU hardware comparisons must be interpreted carefully
- JSONL ingestion may dominate end-to-end runtime
- Parsing and normalization costs can outweigh aggregation costs
- A faster GPU analysis step does not automatically mean the whole pipeline is faster

## What the Synthetic Data Can and Cannot Do

The synthetic data supports benchmarking, repeatability, and architecture comparison. It does not support threat intelligence conclusions, attribution claims, or production deployment validation.

