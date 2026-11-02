"""Read an offline telemetry log and report descriptive statistics."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
import math
from pathlib import Path
import statistics


@dataclass(frozen=True)
class Sample:
    t_s: float
    altitude_m: float
    groundspeed_m_s: float
    mode: str


def read_samples(path):
    samples = []
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError("each record must be a JSON object")
                values = []
                for key in ("t_s", "altitude_m", "groundspeed_m_s"):
                    value = row[key]
                    if isinstance(value, bool) or not isinstance(value, (int, float)):
                        raise ValueError(f"{key} must be a number")
                    if not math.isfinite(value):
                        raise ValueError(f"{key} must be finite")
                    values.append(float(value))
                mode = row["mode"]
                if not isinstance(mode, str) or not mode.strip():
                    raise ValueError("mode must be a non-empty string")
                sample = Sample(*values, mode.strip())
                if sample.t_s < 0 or sample.groundspeed_m_s < 0:
                    raise ValueError("time and groundspeed must be non-negative")
                if samples and sample.t_s <= samples[-1].t_s:
                    raise ValueError("timestamps must be strictly increasing")
                samples.append(sample)
            except (KeyError, ValueError, TypeError, OverflowError) as exc:
                raise ValueError(f"Line {line_number}: {exc}") from exc
    if not samples:
        raise ValueError("No telemetry samples found")
    return samples


def summarize(samples):
    if not samples:
        raise ValueError("No telemetry samples found")
    intervals = []
    durations = defaultdict(float)
    for current, following in zip(samples, samples[1:]):
        interval = following.t_s - current.t_s
        if not math.isfinite(interval) or interval <= 0:
            raise ValueError("timestamps must be finite and strictly increasing")
        intervals.append(interval)
        durations[current.mode] += interval
    result = {
        "sample_count": len(samples),
        "duration_s": samples[-1].t_s - samples[0].t_s,
        "max_sample_interval_s": max(intervals, default=0.0),
        "min_altitude_m": min(row.altitude_m for row in samples),
        "max_altitude_m": max(row.altitude_m for row in samples),
        "max_groundspeed_m_s": max(row.groundspeed_m_s for row in samples),
        "mean_groundspeed_m_s": statistics.fmean(row.groundspeed_m_s for row in samples),
        "mode_sample_counts": dict(sorted(Counter(row.mode for row in samples).items())),
        "mode_durations_s": dict(sorted(durations.items())),
        "last_mode": samples[-1].mode,
    }
    # Reject numerical overflow instead of writing non-standard JSON numbers.
    json.dumps(result, allow_nan=False)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path, help="UTF-8 JSON Lines telemetry file")
    parser.add_argument("--out", type=Path, help="optional JSON output path")
    args = parser.parse_args(argv)
    try:
        if args.out and args.out.resolve() == args.log.resolve():
            raise ValueError("output must not overwrite the input log")
        result = summarize(read_samples(args.log))
        rendered = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
        if args.out:
            args.out.write_text(rendered + "\n", encoding="utf-8")
    except (OSError, ValueError, OverflowError) as exc:
        parser.error(str(exc))
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
