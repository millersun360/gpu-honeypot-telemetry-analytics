# Contribution Model

This repository is designed as a contribution-oriented optimization prototype. It has three layers.

## Layer 1 - Safe Synthetic Benchmark

Purpose:

"Benchmark CPU vs GPU performance on high-volume SSH brute-force aggregation without exposing real attacker IPs or raw honeypot logs."

This layer uses sanitized local Cowrie telemetry to generate synthetic benchmark datasets. It is the safest way to test scale, timing, and output fidelity.

## Layer 2 - Drop-in Local Analyzer

Purpose:

"A tool that a DShield/Cowrie user can run locally against their own Cowrie logs to produce useful summaries without sending raw data anywhere."

Example command:

```powershell
python scripts/analyze_local_cowrie.py --input /srv/cowrie/var/log/cowrie/cowrie.json
```

Expected outputs:

- top usernames
- top passwords
- top credential pairs
- top source IPs
- attempts per time bucket
- high-volume actors
- optional normalized CSV/Parquet export

This layer is where the project becomes most practical for a real user, because it stays local and focuses on summary output that is immediately useful.

## Layer 3 - Accelerated Large-Scale Path

Purpose:

"For larger telemetry volumes, the normalized dataset can be processed using RAPIDS/cuDF and custom CUDA kernels on NVIDIA hardware."

This is where DGX Spark fits. It gives the project a compact accelerated platform for testing whether GPU dataframe processing or custom kernels can reduce analysis time once the telemetry has been normalized.

The long-term idea is straightforward:

- local analyzer for real users
- synthetic benchmark for scale testing
- cuDF for dataframe acceleration
- CUDA for specialized frequency-analysis kernels

