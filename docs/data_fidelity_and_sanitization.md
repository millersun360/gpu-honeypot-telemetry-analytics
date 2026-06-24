# Data Fidelity and Sanitization

This project uses a sanitized local Cowrie sample to build synthetic benchmark datasets. The goal is to preserve the parts of the telemetry that matter for brute-force aggregation while removing or omitting the parts that would create privacy, attribution, or scope problems.

For optimization benchmarking, the sanitized and synthetic dataset is still useful because it preserves the fields required for brute-force aggregation: timestamp, eventid, username, password, source actor, protocol, and port metadata.

For threat intelligence, the dataset is intentionally incomplete. It should not be used for attribution, ASN/geo analysis, bot fingerprinting, session reconstruction, command analysis, malware analysis, or full DShield operational conclusions.

## Preservation and Removal Table

| Field or signal | Preserved / Synthesized / Removed | Purpose | Limitation |
| --- | --- | --- | --- |
| timestamp | Synthesized | Supports ordering, time buckets, and burst analysis | Does not represent a real incident timeline |
| eventid | Synthesized | Distinguishes failed versus successful login events | Only login event types are modeled |
| username | Synthesized | Supports username frequency analysis | Credential distribution is benchmark-oriented, not exhaustive |
| password | Synthesized | Supports password frequency analysis | Credential distribution is benchmark-oriented, not exhaustive |
| protocol | Synthesized | Preserves SSH/Telnet-style protocol mix | Does not model broader service diversity |
| src_ip | Synthesized | Provides source-actor skew and per-IP counting | Synthetic and non-attributable; not a real public IP trace |
| dst_port | Synthesized | Supports port-level summaries | Typically fixed for the benchmark and not a full service map |
| src_port | Synthesized | Preserves per-event network variability | Not meaningful for attribution in this dataset |
| synthetic_actor_id | Synthesized | Stable actor mapping for skew and burstiness | Internal benchmark identifier only |
| uuid | Removed | Not needed for brute-force aggregation | Would add unrelated record identity detail |
| session | Removed | Not needed for the benchmark scope | Prevents session reconstruction claims |
| sensor | Removed | Keeps the dataset local and simplified | Removes deployment-specific context |
| message | Removed | Avoids free-text analysis complexity | Eliminates raw log narrative content |
| key/fingerprint/type | Removed | Excludes cryptographic and metadata fields not needed for the benchmark | Does not support key or fingerprint analysis |
| commands entered | Removed | Keeps scope on login-attempt analytics | Does not support command analysis |
| upload/download events | Removed | Keeps the workload focused on brute-force summaries | Does not model file-transfer behavior |
| HTTP honeypot logs | Removed | Avoids broadening the benchmark beyond SSH login telemetry | Does not represent web-facing honeypot traffic |
| firewall logs | Removed | Keeps the benchmark centered on Cowrie telemetry | Does not model network perimeter analysis |

## What Was Preserved, Synthesized, and Removed

The preserved part of the workload is the analytical shape of SSH brute-force telemetry: repeated credential attempts, source-IP skew, event timing, and port metadata.

The synthesized part is the scale-up dataset. It preserves frequency patterns and actor burstiness without carrying real source IPs or extra operational context.

The removed part is everything outside the narrow benchmark scope, especially session detail, command streams, malware artifacts, and unrelated telemetry sources.

## Did Sanitization Drift Too Far?

No for performance benchmarking of SSH credential-attempt aggregation. Yes for full threat intelligence or production DShield analytics.

That is the correct tradeoff for this project because the point is to evaluate acceleration on a bounded, privacy-preserving workload rather than to reconstruct the full investigative environment.

