#!/usr/bin/env python3
"""
Synthetic Cowrie benchmark generator.

This script creates synthetic Cowrie-style JSONL for benchmarking only.
The output is not real attacker data, and it must not be used to make
claims about live adversary behavior.
"""

from __future__ import annotations

import argparse
import bisect
import gzip
import json
import math
import random
import sys
import time
import ipaddress
from collections import Counter, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator


FALLBACK_USERNAMES = [
    "root",
    "admin",
    "user",
    "ubuntu",
    "test",
    "oracle",
    "postgres",
    "mysql",
    "guest",
    "support",
    "deploy",
    "ftp",
    "pi",
    "debian",
    "ec2-user",
    "azureuser",
    "cloud-user",
    "git",
    "jenkins",
    "minecraft",
    "runner",
    "node",
    "www",
]

FALLBACK_PASSWORDS = [
    "123456",
    "123",
    "1234",
    "1",
    "12345678",
    "admin",
    "password",
    "root",
    "12345",
    "123456789",
    "111111",
    "abc123",
    "test",
    "qwerty",
    "toor",
    "passwd",
    "123123",
    "123321",
    "ubuntu",
    "changeme",
    "password1",
    "admin123",
    "P@ssw0rd",
    "raspberry",
]

FALLBACK_PAIR_WEIGHTS = [
    ("root", "123456", 24),
    ("root", "root", 16),
    ("admin", "admin", 22),
    ("admin", "123456", 16),
    ("admin", "password", 12),
    ("root", "password", 12),
    ("user", "password", 10),
    ("ubuntu", "ubuntu", 10),
    ("test", "test", 10),
    ("guest", "password", 8),
    ("pi", "raspberry", 8),
    ("postgres", "12345678", 8),
    ("mysql", "123456", 8),
    ("support", "changeme", 6),
    ("deploy", "password1", 6),
    ("ftp", "123456", 6),
    ("debian", "admin123", 6),
    ("runner", "1234", 6),
    ("node", "12345", 6),
    ("minecraft", "abc123", 6),
    ("ec2-user", "P@ssw0rd", 6),
    ("azureuser", "password1", 6),
    ("cloud-user", "changeme", 6),
    ("git", "toor", 6),
    ("jenkins", "123321", 6),
    ("www", "111111", 6),
    ("root", "admin", 6),
    ("test", "123456", 6),
]

FALLBACK_EVENTIDS = [
    ("cowrie.login.failed", 95),
    ("cowrie.login.success", 5),
]

FALLBACK_PROTOCOLS = [
    ("ssh", 95),
    ("telnet", 5),
]

FALLBACK_PORTS_BY_PROTOCOL = {
    "ssh": [(22, 90), (2222, 10)],
    "telnet": [(23, 90), (2323, 10)],
}

DEFAULT_PROGRESS_INTERVAL = 100_000
DEFAULT_WINDOW_DAYS = 7
DEFAULT_BUCKET_MINUTES = 5
DEFAULT_DST_PORT = 2222
DEFAULT_NOISY_ACTOR_RATIO = 0.05
DEFAULT_MEDIUM_ACTOR_RATIO = 0.20
DEFAULT_SRC_IP_MODE = "private-diverse"


@dataclass(frozen=True)
class WeightedSampler:
    items: tuple[Any, ...]
    cum_weights: tuple[float, ...]
    total: float

    def choice(self, rng: random.Random) -> Any:
        if not self.items:
            raise ValueError("sampler has no items")
        r = rng.random() * self.total
        index = bisect.bisect_left(self.cum_weights, r)
        if index >= len(self.items):
            index = len(self.items) - 1
        return self.items[index]


@dataclass
class SampleStats:
    total_records: int
    eventid_counts: Counter[str]
    username_counts: Counter[str]
    password_counts: Counter[str]
    protocol_counts: Counter[str]
    pair_counts: Counter[tuple[str, str]]
    port_counts_by_protocol: dict[str, Counter[int]]
    min_timestamp: datetime | None
    max_timestamp: datetime | None
    observed_username_values: set[str]
    observed_password_values: set[str]


@contextmanager
def open_text(path: str, mode: str):
    if path == "-":
        if "r" in mode:
            yield sys.stdin
        else:
            yield sys.stdout
        return

    if path.endswith(".gz"):
        with gzip.open(path, mode + "t", encoding="utf-8", newline="") as handle:
            yield handle
        return

    with Path(path).open(mode, encoding="utf-8", newline="") as handle:
        yield handle


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None

    normalized = text.replace("Z", "+00:00")
    if len(normalized) >= 5 and normalized[-5] in "+-" and normalized[-3] != ":":
        normalized = normalized[:-2] + ":" + normalized[-2:]

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def build_sampler(items_with_weights: Iterable[tuple[Any, int]]) -> WeightedSampler:
    items: list[Any] = []
    cum_weights: list[float] = []
    total = 0.0
    for item, weight in items_with_weights:
        if weight <= 0:
            continue
        total += float(weight)
        items.append(item)
        cum_weights.append(total)

    return WeightedSampler(tuple(items), tuple(cum_weights), total)


def parse_csv_set(value: str | None) -> set[str]:
    if not value:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def normalize_exclusions(
    excluded_usernames: set[str], excluded_passwords: set[str], excluded_values: set[str]
) -> tuple[set[str], set[str], set[str]]:
    username_exclusions = set(excluded_usernames) | set(excluded_values)
    password_exclusions = set(excluded_passwords) | set(excluded_values)
    broad_exclusions = username_exclusions | password_exclusions
    return username_exclusions, password_exclusions, broad_exclusions


def choose_eventid_sampler(stats: SampleStats, profile: str) -> WeightedSampler:
    observed = build_sampler(stats.eventid_counts.items()) if stats.eventid_counts else None
    if profile == "observed":
        if observed is not None and observed.total > 0:
            return observed
        return build_sampler(FALLBACK_EVENTIDS)

    if profile == "brute-force":
        return build_sampler([("cowrie.login.failed", 95), ("cowrie.login.success", 5)])

    if profile == "failed-heavy":
        return build_sampler([("cowrie.login.failed", 99), ("cowrie.login.success", 1)])

    raise ValueError(f"unknown profile: {profile}")


def choose_protocol_sampler(stats: SampleStats) -> WeightedSampler:
    if stats.protocol_counts:
        return build_sampler(stats.protocol_counts.items())
    return build_sampler(FALLBACK_PROTOCOLS)


def filter_stats_for_exclusions(
    stats: SampleStats, excluded_usernames: set[str], excluded_passwords: set[str]
) -> tuple[WeightedSampler | None, WeightedSampler | None, WeightedSampler | None]:
    observed_usernames = Counter({k: v for k, v in stats.username_counts.items() if k not in excluded_usernames})
    observed_passwords = Counter({k: v for k, v in stats.password_counts.items() if k not in excluded_passwords})

    observed_pairs = Counter(
        {
            pair: count
            for pair, count in stats.pair_counts.items()
            if pair[0] not in excluded_usernames and pair[1] not in excluded_passwords
        }
    )

    username_sampler = build_sampler(observed_usernames.items()) if observed_usernames else None
    password_sampler = build_sampler(observed_passwords.items()) if observed_passwords else None
    pair_sampler = build_sampler(observed_pairs.items()) if observed_pairs else None
    return username_sampler, password_sampler, pair_sampler


def choose_fallback_pair_sampler(
    excluded_usernames: set[str], excluded_passwords: set[str]
) -> WeightedSampler | None:
    items = [
        ((username, password), weight)
        for username, password, weight in FALLBACK_PAIR_WEIGHTS
        if username not in excluded_usernames and password not in excluded_passwords
    ]
    return build_sampler(items) if items else None


def choose_fallback_username_sampler(excluded_usernames: set[str]) -> WeightedSampler | None:
    items = [(item, 1) for item in FALLBACK_USERNAMES if item not in excluded_usernames]
    return build_sampler(items) if items else None


def choose_fallback_password_sampler(excluded_passwords: set[str]) -> WeightedSampler | None:
    items = [(item, 1) for item in FALLBACK_PASSWORDS if item not in excluded_passwords]
    return build_sampler(items) if items else None


def build_allowed_credential_sets(
    stats: SampleStats, excluded_usernames: set[str], excluded_passwords: set[str]
) -> tuple[set[str], set[str]]:
    allowed_usernames = set(stats.observed_username_values)
    allowed_passwords = set(stats.observed_password_values)

    allowed_usernames.difference_update(excluded_usernames)
    allowed_passwords.difference_update(excluded_passwords)

    for username in FALLBACK_USERNAMES:
        if username not in excluded_usernames:
            allowed_usernames.add(username)
    for password in FALLBACK_PASSWORDS:
        if password not in excluded_passwords:
            allowed_passwords.add(password)

    return allowed_usernames, allowed_passwords


def choose_credential_pair(
    rng: random.Random,
    observed_pair_sampler: WeightedSampler | None,
    observed_username_sampler: WeightedSampler | None,
    observed_password_sampler: WeightedSampler | None,
    fallback_pair_sampler: WeightedSampler | None,
    fallback_username_sampler: WeightedSampler | None,
    fallback_password_sampler: WeightedSampler | None,
) -> tuple[str, str]:
    options: list[tuple[str, int]] = []
    if observed_pair_sampler is not None and observed_pair_sampler.total > 0:
        options.append(("observed_pair", 50))
    if (
        observed_username_sampler is not None
        and observed_username_sampler.total > 0
        and observed_password_sampler is not None
        and observed_password_sampler.total > 0
    ):
        options.append(("observed_independent", 30))
    if fallback_pair_sampler is not None and fallback_pair_sampler.total > 0:
        options.append(("fallback_pair", 20))

    if not options:
        if fallback_username_sampler is not None and fallback_password_sampler is not None:
            return fallback_username_sampler.choice(rng), fallback_password_sampler.choice(rng)
        if observed_username_sampler is not None and observed_password_sampler is not None:
            return observed_username_sampler.choice(rng), observed_password_sampler.choice(rng)
        if fallback_pair_sampler is not None and fallback_pair_sampler.total > 0:
            return fallback_pair_sampler.choice(rng)
        raise ValueError("no credential sources available")

    mode = build_sampler(options).choice(rng)
    if mode == "observed_pair" and observed_pair_sampler is not None:
        return observed_pair_sampler.choice(rng)
    if mode == "observed_independent" and observed_username_sampler is not None and observed_password_sampler is not None:
        return observed_username_sampler.choice(rng), observed_password_sampler.choice(rng)
    if mode == "fallback_pair" and fallback_pair_sampler is not None:
        return fallback_pair_sampler.choice(rng)

    if observed_username_sampler is not None and observed_password_sampler is not None:
        return observed_username_sampler.choice(rng), observed_password_sampler.choice(rng)
    if fallback_username_sampler is not None and fallback_password_sampler is not None:
        return fallback_username_sampler.choice(rng), fallback_password_sampler.choice(rng)
    if fallback_pair_sampler is not None and fallback_pair_sampler.total > 0:
        return fallback_pair_sampler.choice(rng)
    raise ValueError("no credential sources available")


def build_port_samplers(stats: SampleStats) -> dict[str, WeightedSampler]:
    samplers: dict[str, WeightedSampler] = {}
    for protocol, counter in stats.port_counts_by_protocol.items():
        if counter:
            samplers[protocol] = build_sampler(counter.items())
    for protocol, values in FALLBACK_PORTS_BY_PROTOCOL.items():
        if protocol not in samplers:
            samplers[protocol] = build_sampler(values)
    return samplers


def default_actor_count(record_count: int) -> int:
    # Scales to the requested benchmark size while staying inside a practical private-IP pool.
    return min(max(record_count // 20, 500), 100_000)


def make_private_10_ip(actor_index: int) -> str:
    value = actor_index + 1
    second = (value >> 16) & 0xFF
    third = (value >> 8) & 0xFF
    fourth = value & 0xFF
    if fourth == 0:
        fourth = 1
    return f"10.{second}.{third}.{fourth}"


def make_private_172_ip(actor_index: int) -> str:
    value = actor_index
    third = (value >> 8) & 0xFF
    fourth = value & 0xFF
    second = 16 + ((value >> 16) % 16)
    if fourth == 0:
        fourth = 1
    return f"172.{second}.{third}.{fourth}"


def make_private_192_ip(actor_index: int) -> str:
    value = actor_index + 1
    third = (value >> 8) & 0xFF
    fourth = value & 0xFF
    if fourth == 0:
        fourth = 1
    return f"192.168.{third}.{fourth}"


def make_documentation_ip(actor_index: int) -> str:
    ranges = ("192.0.2", "198.51.100", "203.0.113")
    prefix = ranges[actor_index % len(ranges)]
    host = (actor_index // len(ranges)) % 254 + 1
    return f"{prefix}.{host}"


def split_actor_pool(actor_count: int, noisy_actor_ratio: float) -> tuple[int, int, int]:
    if actor_count <= 0:
        return (0, 0, 0)
    if actor_count == 1:
        return (1, 0, 0)
    if actor_count == 2:
        return (1, 1, 0)

    noisy = max(1, int(round(actor_count * noisy_actor_ratio)))
    medium = max(1, int(round(actor_count * DEFAULT_MEDIUM_ACTOR_RATIO)))

    if noisy + medium >= actor_count:
        medium = max(1, actor_count - noisy - 1)
    tail = max(1, actor_count - noisy - medium)

    total = noisy + medium + tail
    if total != actor_count:
        tail += actor_count - total

    return noisy, medium, tail


def weighted_private_range_sequence(actor_count: int, rng: random.Random) -> list[str]:
    sequence: list[str] = []
    ranges = ["10", "172", "192"]
    weights = [70, 20, 10]
    sampler = build_sampler(zip(ranges, weights))
    for _ in range(actor_count):
        sequence.append(sampler.choice(rng))
    return sequence


def build_actor_sampler(
    actor_count: int, noisy_actor_ratio: float, src_ip_mode: str, rng: random.Random
) -> tuple[list[str], WeightedSampler]:
    noisy_count, medium_count, tail_count = split_actor_pool(actor_count, noisy_actor_ratio)

    ips: list[str] = []
    weights: list[float] = []
    private_range_choices: list[str] = []

    if src_ip_mode == "private-diverse":
        private_range_choices = weighted_private_range_sequence(actor_count, rng)

    def add_group(count: int, total_mass: float, alpha: float, weight_floor: float, jitter: tuple[float, float]) -> None:
        start_index = len(ips)
        raw_weights: list[float] = []
        for rank in range(1, count + 1):
            base = total_mass / (rank**alpha)
            raw_weights.append(max(weight_floor, base * rng.uniform(*jitter)))

        scale = 1_000_000
        for offset, raw_weight in enumerate(raw_weights):
            actor_index = start_index + offset
            if src_ip_mode == "private-10":
                ip = make_private_10_ip(actor_index)
            elif src_ip_mode == "private-diverse":
                selected = private_range_choices[actor_index]
                if selected == "10":
                    ip = make_private_10_ip(actor_index)
                elif selected == "172":
                    ip = make_private_172_ip(actor_index)
                else:
                    ip = make_private_192_ip(actor_index)
            elif src_ip_mode == "documentation":
                ip = make_documentation_ip(actor_index)
            else:
                raise ValueError(f"unsupported src-ip-mode: {src_ip_mode}")
            ips.append(ip)
            weights.append(int(raw_weight * scale) + 1)

    add_group(noisy_count, total_mass=0.55, alpha=0.55, weight_floor=0.75, jitter=(0.90, 1.20))
    add_group(medium_count, total_mass=0.30, alpha=0.90, weight_floor=0.20, jitter=(0.85, 1.15))
    add_group(tail_count, total_mass=0.15, alpha=1.20, weight_floor=0.05, jitter=(0.80, 1.20))

    sampler = build_sampler(zip(range(len(ips)), weights))
    return ips, sampler


def classify_src_ip(value: str) -> str:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return "public/non-private"

    if ip.version != 4:
        return "other/private"

    text = str(ip)
    if text.startswith("10."):
        return "10.0.0.0/8"
    if text.startswith("172.") and 16 <= int(text.split(".")[1]) <= 31:
        return "172.16.0.0/12"
    if text.startswith("192.168."):
        return "192.168.0.0/16"
    if text.startswith("192.0.2.") or text.startswith("198.51.100.") or text.startswith("203.0.113."):
        return "documentation"

    if ip.is_private or ip.is_reserved:
        return "other/private"
    return "public/non-private"


def build_bucket_weights(
    start: datetime, days: int, bucket_minutes: int, rng: random.Random
) -> tuple[list[datetime], list[float]]:
    bucket_seconds = bucket_minutes * 60
    bucket_count = max(1, int(days * 24 * 60 / bucket_minutes))
    bucket_starts = [start + timedelta(seconds=bucket_seconds * i) for i in range(bucket_count)]
    weights: list[float] = []

    burst_centers = set()
    burst_total = max(8, bucket_count // 16)
    for _ in range(burst_total):
        burst_centers.add(rng.randrange(bucket_count))

    for i, bucket_start in enumerate(bucket_starts):
        minute_of_day = bucket_start.hour * 60 + bucket_start.minute
        circadian = 1.0 + 0.28 * math.sin((minute_of_day / 1440.0) * 2.0 * math.pi - 0.7)
        circadian += 0.12 * math.sin((minute_of_day / 720.0) * 2.0 * math.pi + 0.3)
        circadian = max(0.25, circadian)

        if i in burst_centers:
            burst = rng.uniform(2.5, 8.0)
        else:
            burst = rng.uniform(0.85, 1.25)
            if rng.random() < 0.10:
                burst *= rng.uniform(1.25, 2.25)

        jitter = rng.uniform(0.85, 1.15)
        weights.append(max(0.001, circadian * burst * jitter))

    return bucket_starts, weights


def allocate_counts(total_records: int, weights: list[float]) -> list[int]:
    if total_records <= 0:
        return [0 for _ in weights]

    weight_sum = sum(weights)
    if weight_sum <= 0:
        base = total_records // len(weights)
        counts = [base for _ in weights]
        for i in range(total_records - base * len(weights)):
            counts[i % len(counts)] += 1
        return counts

    expected = [w * total_records / weight_sum for w in weights]
    counts = [int(x) for x in expected]
    remainder = total_records - sum(counts)
    if remainder <= 0:
        return counts

    order = sorted(
        range(len(weights)),
        key=lambda i: (expected[i] - counts[i], weights[i]),
        reverse=True,
    )
    for i in order[:remainder]:
        counts[i] += 1
    return counts


def load_sample(
    path: str,
    excluded_usernames: set[str] | None = None,
    excluded_passwords: set[str] | None = None,
) -> SampleStats:
    eventid_counts: Counter[str] = Counter()
    username_counts: Counter[str] = Counter()
    password_counts: Counter[str] = Counter()
    protocol_counts: Counter[str] = Counter()
    pair_counts: Counter[tuple[str, str]] = Counter()
    port_counts_by_protocol: dict[str, Counter[int]] = defaultdict(Counter)
    min_timestamp: datetime | None = None
    max_timestamp: datetime | None = None
    total_records = 0
    observed_username_values: set[str] = set()
    observed_password_values: set[str] = set()

    excluded_usernames = excluded_usernames or set()
    excluded_passwords = excluded_passwords or set()

    with open_text(path, "r") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.lstrip("\ufeff").strip()
            if not text:
                continue

            try:
                record = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc

            if not isinstance(record, dict):
                continue

            total_records += 1

            eventid = record.get("eventid")
            if isinstance(eventid, str) and eventid:
                eventid_counts[eventid] += 1

            protocol = record.get("protocol")
            if isinstance(protocol, str) and protocol:
                protocol_counts[protocol] += 1

            if eventid in {"cowrie.login.success", "cowrie.login.failed"}:
                username = record.get("username")
                if isinstance(username, str) and username and username not in excluded_usernames:
                    observed_username_values.add(username)
                    username_counts[username] += 1

                password = record.get("password")
                if isinstance(password, str) and password and password not in excluded_passwords:
                    observed_password_values.add(password)
                    password_counts[password] += 1

                if (
                    isinstance(username, str)
                    and username
                    and isinstance(password, str)
                    and password
                    and username not in excluded_usernames
                    and password not in excluded_passwords
                ):
                    pair_counts[(username, password)] += 1

            dst_port = record.get("dst_port")
            if isinstance(dst_port, int) and 0 < dst_port < 65536:
                if isinstance(protocol, str) and protocol:
                    port_counts_by_protocol[protocol][dst_port] += 1

            ts = parse_timestamp(record.get("timestamp"))
            if ts is not None:
                if min_timestamp is None or ts < min_timestamp:
                    min_timestamp = ts
                if max_timestamp is None or ts > max_timestamp:
                    max_timestamp = ts

    if total_records == 0:
        raise ValueError("No usable JSON records were found in the input file")

    return SampleStats(
        total_records=total_records,
        eventid_counts=eventid_counts,
        username_counts=username_counts,
        password_counts=password_counts,
        protocol_counts=protocol_counts,
        pair_counts=pair_counts,
        port_counts_by_protocol=port_counts_by_protocol,
        min_timestamp=min_timestamp,
        max_timestamp=max_timestamp,
        observed_username_values=observed_username_values,
        observed_password_values=observed_password_values,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate synthetic Cowrie-style JSONL from a sanitized Cowrie sample."
    )
    parser.add_argument("--input", required=True, help="Sanitized Cowrie JSONL input file. .gz is supported.")
    parser.add_argument("--output", required=True, help="Synthetic JSONL output file. .gz is supported.")
    parser.add_argument(
        "--records",
        type=int,
        default=10_000_000,
        help="Number of synthetic records to generate. Default: 10,000,000.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Deterministic random seed.")
    parser.add_argument(
        "--dst-port",
        type=int,
        default=DEFAULT_DST_PORT,
        help="Synthetic destination port to emit. Default: 2222.",
    )
    parser.add_argument(
        "--profile",
        choices=("observed", "brute-force", "failed-heavy"),
        default="observed",
        help="Eventid profile to generate.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_WINDOW_DAYS,
        help="Synthetic time window in days. Default: 7.",
    )
    parser.add_argument(
        "--start",
        default=None,
        help="Synthetic start timestamp in ISO 8601 UTC, for example 2026-06-22T00:00:00Z.",
    )
    parser.add_argument(
        "--progress-interval",
        type=int,
        default=DEFAULT_PROGRESS_INTERVAL,
        help="Print progress every N records. Default: 100,000. Use 0 to disable.",
    )
    parser.add_argument(
        "--actors",
        type=int,
        default=None,
        help="Total synthetic source-IP actors to generate. Default scales with record count.",
    )
    parser.add_argument(
        "--noisy-actor-ratio",
        type=float,
        default=DEFAULT_NOISY_ACTOR_RATIO,
        help="Fraction of actors assigned to the noisy/high-volume group. Default: 0.05.",
    )
    parser.add_argument(
        "--exclude-usernames",
        default="",
        help="Comma-separated observed usernames to exclude from synthetic output.",
    )
    parser.add_argument(
        "--exclude-passwords",
        default="",
        help="Comma-separated observed passwords to exclude from synthetic output.",
    )
    parser.add_argument(
        "--exclude-values",
        default="",
        help="Comma-separated values to exclude from both username and password generation.",
    )
    parser.add_argument(
        "--allow-unexpected-values",
        action="store_true",
        help="Allow generated usernames/passwords that fall outside the observed+fallback vocabulary.",
    )
    parser.add_argument(
        "--sort-by-time",
        action="store_true",
        help="Sort records by timestamp within each time bucket before writing.",
    )
    parser.add_argument(
        "--src-ip-mode",
        choices=("private-diverse", "private-10", "documentation"),
        default=DEFAULT_SRC_IP_MODE,
        help="Synthetic source-IP mode. Default: private-diverse.",
    )
    return parser


def generate_records(
    stats: SampleStats,
    total_records: int,
    profile: str,
    days: int,
    start: datetime,
    dst_port: int,
    actor_count: int | None,
    noisy_actor_ratio: float,
    sort_by_time: bool,
    observed_username_sampler: WeightedSampler | None,
    observed_password_sampler: WeightedSampler | None,
    observed_pair_sampler: WeightedSampler | None,
    fallback_username_sampler: WeightedSampler | None,
    fallback_password_sampler: WeightedSampler | None,
    fallback_pair_sampler: WeightedSampler | None,
    src_ip_mode: str,
    rng: random.Random,
) -> Iterator[dict[str, Any]]:
    eventid_sampler = choose_eventid_sampler(stats, profile)
    protocol_sampler = choose_protocol_sampler(stats)

    if actor_count is None:
        actor_count = default_actor_count(total_records)
    actor_ips, actor_sampler = build_actor_sampler(actor_count, noisy_actor_ratio, src_ip_mode, rng)

    bucket_starts, bucket_weights = build_bucket_weights(start, days, DEFAULT_BUCKET_MINUTES, rng)
    bucket_counts = allocate_counts(total_records, bucket_weights)

    produced = 0
    for bucket_start, bucket_count in zip(bucket_starts, bucket_counts):
        if bucket_count <= 0:
            continue

        bucket_records: list[dict[str, Any]] = []
        for _ in range(bucket_count):
            eventid = eventid_sampler.choice(rng)
            protocol = protocol_sampler.choice(rng)

            username, password = choose_credential_pair(
                rng=rng,
                observed_pair_sampler=observed_pair_sampler,
                observed_username_sampler=observed_username_sampler,
                observed_password_sampler=observed_password_sampler,
                fallback_pair_sampler=fallback_pair_sampler,
                fallback_username_sampler=fallback_username_sampler,
                fallback_password_sampler=fallback_password_sampler,
            )

            actor_id = int(actor_sampler.choice(rng))
            src_ip = actor_ips[actor_id]
            src_port = rng.randint(1_024, 65_535)

            timestamp = bucket_start + timedelta(seconds=rng.uniform(0, DEFAULT_BUCKET_MINUTES * 60))
            bucket_records.append(
                {
                    "timestamp": format_timestamp(timestamp),
                    "eventid": eventid,
                    "src_ip": src_ip,
                    "username": username,
                    "password": password,
                    "protocol": protocol,
                    "dst_port": dst_port,
                    "src_port": src_port,
                    "synthetic_actor_id": actor_id,
                }
            )

            produced += 1
            if produced >= total_records:
                break

        if sort_by_time:
            bucket_records.sort(key=lambda item: item["timestamp"])

        for record in bucket_records:
            yield record

        if produced >= total_records:
            return


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    excluded_usernames = parse_csv_set(args.exclude_usernames)
    excluded_passwords = parse_csv_set(args.exclude_passwords)
    excluded_values = parse_csv_set(args.exclude_values)
    excluded_usernames, excluded_passwords, _ = normalize_exclusions(
        excluded_usernames, excluded_passwords, excluded_values
    )

    if args.records <= 0:
        parser.error("--records must be positive")
    if args.days <= 0:
        parser.error("--days must be positive")
    if args.progress_interval < 0:
        parser.error("--progress-interval must be zero or positive")
    if not (1 <= args.dst_port <= 65535):
        parser.error("--dst-port must be between 1 and 65535")
    if args.actors is not None and args.actors <= 0:
        parser.error("--actors must be positive when provided")
    if not (0.0 < args.noisy_actor_ratio < 1.0):
        parser.error("--noisy-actor-ratio must be between 0 and 1")
    if args.src_ip_mode == "documentation" and args.actors is None and args.records >= 1_000_000:
        print(
            "generate_synthetic_cowrie: documentation src-ip mode is not recommended for large benchmark datasets",
            file=sys.stderr,
        )

    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(2**63)
    rng = random.Random(seed)

    try:
        stats = load_sample(args.input, excluded_usernames, excluded_passwords)
    except Exception as exc:
        parser.exit(2, f"generate_synthetic_cowrie: {exc}\n")

    if args.start:
        start = parse_timestamp(args.start)
        if start is None:
            parser.error("--start must be an ISO 8601 UTC timestamp such as 2026-06-22T00:00:00Z")
    elif stats.min_timestamp is not None:
        start = stats.min_timestamp
    else:
        start = datetime.now(timezone.utc)

    observed_username_sampler, observed_password_sampler, observed_pair_sampler = filter_stats_for_exclusions(
        stats, excluded_usernames, excluded_passwords
    )
    fallback_username_sampler = choose_fallback_username_sampler(excluded_usernames)
    fallback_password_sampler = choose_fallback_password_sampler(excluded_passwords)
    fallback_pair_sampler = choose_fallback_pair_sampler(excluded_usernames, excluded_passwords)
    allowed_usernames, allowed_passwords = build_allowed_credential_sets(
        stats, excluded_usernames, excluded_passwords
    )

    output_path = Path(args.output)
    if output_path != Path("-"):
        output_path.parent.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    eventid_counts: Counter[str] = Counter()
    username_counts: Counter[str] = Counter()
    password_counts: Counter[str] = Counter()
    credential_counts: Counter[tuple[str, str]] = Counter()
    src_ip_counts: Counter[str] = Counter()
    min_generated_timestamp: datetime | None = None
    max_generated_timestamp: datetime | None = None
    unexpected_samples: list[str] = []
    unexpected_count = 0
    excluded_username_counts: Counter[str] = Counter()
    excluded_password_counts: Counter[str] = Counter()
    public_src_ip_count = 0
    written = 0
    unique_src_ips = 0
    range_counts: Counter[str] = Counter()

    try:
        with open_text(args.output, "w") as handle:
            for record in generate_records(
                stats=stats,
                total_records=args.records,
                profile=args.profile,
                days=args.days,
                start=start,
                dst_port=args.dst_port,
                actor_count=args.actors,
                noisy_actor_ratio=args.noisy_actor_ratio,
                sort_by_time=args.sort_by_time,
                observed_username_sampler=observed_username_sampler,
                observed_password_sampler=observed_password_sampler,
                observed_pair_sampler=observed_pair_sampler,
                fallback_username_sampler=fallback_username_sampler,
                fallback_password_sampler=fallback_password_sampler,
                fallback_pair_sampler=fallback_pair_sampler,
                src_ip_mode=args.src_ip_mode,
                rng=rng,
            ):
                handle.write(json.dumps(record, separators=(",", ":"), ensure_ascii=False))
                handle.write("\n")
                written += 1
                eventid_counts[record["eventid"]] += 1
                username_counts[record["username"]] += 1
                password_counts[record["password"]] += 1
                credential_counts[(record["username"], record["password"])] += 1
                src_ip_counts[record["src_ip"]] += 1
                unique_src_ips = len(src_ip_counts)
                range_counts[classify_src_ip(record["src_ip"])] += 1
                ts = parse_timestamp(record.get("timestamp"))
                if ts is not None:
                    if min_generated_timestamp is None or ts < min_generated_timestamp:
                        min_generated_timestamp = ts
                    if max_generated_timestamp is None or ts > max_generated_timestamp:
                        max_generated_timestamp = ts

                if record["username"] in excluded_usernames:
                    excluded_username_counts[record["username"]] += 1
                if record["password"] in excluded_passwords:
                    excluded_password_counts[record["password"]] += 1

                if record["username"] not in allowed_usernames:
                    unexpected_count += 1
                    if len(unexpected_samples) < 50:
                        unexpected_samples.append(f"username={record['username']}")
                if record["password"] not in allowed_passwords:
                    unexpected_count += 1
                    if len(unexpected_samples) < 50:
                        unexpected_samples.append(f"password={record['password']}")

                try:
                    ip_obj = ipaddress.ip_address(record["src_ip"])
                    if not ip_obj.is_private and not ip_obj.is_reserved:
                        public_src_ip_count += 1
                except ValueError:
                    public_src_ip_count += 1

                if args.progress_interval and written % args.progress_interval == 0:
                    print(
                        f"generate_synthetic_cowrie: wrote {written:,}/{args.records:,} records",
                        file=sys.stderr,
                    )
    except BrokenPipeError:
        return 0

    elapsed = time.perf_counter() - started
    size_text = "n/a"
    if output_path != Path("-") and output_path.exists():
        size_bytes = output_path.stat().st_size
        size_text = f"{size_bytes / (1024 * 1024):.2f} MiB"

    print(f"records written: {written:,}", file=sys.stderr)
    print(f"output path: {args.output}", file=sys.stderr)
    print(f"elapsed time: {elapsed:.2f} seconds", file=sys.stderr)
    print(f"approximate file size: {size_text}", file=sys.stderr)
    print(f"destination port used: {args.dst_port}", file=sys.stderr)
    print(f"source IP mode: {args.src_ip_mode}", file=sys.stderr)
    print(f"excluded values: {', '.join(sorted(excluded_values)) if excluded_values else 'none'}", file=sys.stderr)
    print(f"excluded usernames: {', '.join(sorted(excluded_usernames)) if excluded_usernames else 'none'}", file=sys.stderr)
    print(f"excluded passwords: {', '.join(sorted(excluded_passwords)) if excluded_passwords else 'none'}", file=sys.stderr)
    print("eventid counts:", file=sys.stderr)
    for eventid, count in eventid_counts.most_common():
        print(f"  {eventid}: {count:,}", file=sys.stderr)
    print(f"unique synthetic source IPs: {unique_src_ips:,}", file=sys.stderr)
    print("source IP range counts:", file=sys.stderr)
    for label in [
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "documentation",
        "other/private",
        "public/non-private",
    ]:
        print(f"  {label}: {range_counts.get(label, 0):,}", file=sys.stderr)
    print(
        "timestamp min/max: "
        + (
            f"{format_timestamp(min_generated_timestamp)} / {format_timestamp(max_generated_timestamp)}"
            if min_generated_timestamp is not None and max_generated_timestamp is not None
            else "n/a"
        ),
        file=sys.stderr,
    )
    print("top 20 usernames:", file=sys.stderr)
    for username, count in username_counts.most_common(20):
        print(f"  {username}: {count:,}", file=sys.stderr)
    print("top 20 passwords:", file=sys.stderr)
    for password, count in password_counts.most_common(20):
        print(f"  {password}: {count:,}", file=sys.stderr)
    print("top 20 credential pairs:", file=sys.stderr)
    for (username, password), count in credential_counts.most_common(20):
        print(f"  {username} / {password}: {count:,}", file=sys.stderr)
    print("top 20 source IPs:", file=sys.stderr)
    for src_ip, count in src_ip_counts.most_common(20):
        print(f"  {src_ip}: {count:,}", file=sys.stderr)
    print(f"excluded usernames generated: {sum(excluded_username_counts.values()):,}", file=sys.stderr)
    print(f"excluded passwords generated: {sum(excluded_password_counts.values()):,}", file=sys.stderr)
    print(f"unexpected usernames/passwords outside observed+fallback: {unexpected_count:,}", file=sys.stderr)
    print(f"public/non-private generated source IPs: {public_src_ip_count:,}", file=sys.stderr)

    excluded_total = sum(excluded_username_counts.values()) + sum(excluded_password_counts.values())
    if excluded_total and not args.allow_unexpected_values:
        print("excluded values generated:", file=sys.stderr)
        for value, count in excluded_username_counts.most_common(50):
            print(f"  {value} (username): {count:,}", file=sys.stderr)
        for value, count in excluded_password_counts.most_common(50):
            print(f"  {value} (password): {count:,}", file=sys.stderr)
        parser.exit(3, "generate_synthetic_cowrie: excluded values were generated\n")

    if unexpected_count and not args.allow_unexpected_values:
        if unexpected_samples:
            print("unexpected values (first 50):", file=sys.stderr)
            for item in unexpected_samples[:50]:
                print(f"  {item}", file=sys.stderr)
        parser.exit(3, "generate_synthetic_cowrie: unexpected username/password values were generated\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
