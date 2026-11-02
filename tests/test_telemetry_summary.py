import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from telemetry_summary import Sample, main, read_samples, summarize


ROOT = Path(__file__).resolve().parents[1]


class TelemetryTests(unittest.TestCase):
    def read_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "log.jsonl"
            path.write_text(text, encoding="utf-8")
            return read_samples(path)

    def test_sample_result_and_mode_intervals(self):
        result = summarize(read_samples(ROOT / "examples/synthetic_telemetry.jsonl"))
        self.assertEqual(result["sample_count"], 6)
        self.assertEqual(result["duration_s"], 10)
        self.assertEqual(result["max_altitude_m"], 25)
        self.assertAlmostEqual(result["mean_groundspeed_m_s"], 38 / 6)
        self.assertEqual(result["mode_durations_s"], {
            "GROUND": 2, "TAKEOFF": 2, "CRUISE": 4, "LANDING": 2,
        })
        self.assertEqual(result["mode_sample_counts"]["GROUND"], 2)

    def test_duration_does_not_require_zero_start(self):
        rows = [Sample(100, 3, 2, "IDLE"), Sample(103, 4, 3, "END")]
        self.assertEqual(summarize(rows)["duration_s"], 3)

    def test_one_sample_has_zero_duration(self):
        result = summarize([Sample(20, -1, 0, "IDLE")])
        self.assertEqual(result["duration_s"], 0)
        self.assertEqual(result["mode_durations_s"], {})

    def test_invalid_fields_report_the_line(self):
        valid = {"t_s": 0, "altitude_m": 0, "groundspeed_m_s": 0, "mode": "IDLE"}
        invalid = [
            {**valid, "t_s": True},
            {**valid, "altitude_m": float("nan")},
            {**valid, "groundspeed_m_s": -1},
            {**valid, "mode": " "},
            {"t_s": 0},
            [],
        ]
        for row in invalid:
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, "Line 2"):
                self.read_text("\n" + json.dumps(row))

    def test_duplicate_and_reversed_times_are_rejected(self):
        for times in ([1, 1], [2, 1]):
            rows = [{"t_s": t, "altitude_m": 0, "groundspeed_m_s": 0, "mode": "IDLE"} for t in times]
            with self.subTest(times=times), self.assertRaisesRegex(ValueError, "strictly increasing"):
                self.read_text("\n".join(map(json.dumps, rows)))

    def test_empty_and_malformed_logs(self):
        with self.assertRaisesRegex(ValueError, "No telemetry"):
            self.read_text("\n\n")
        with self.assertRaisesRegex(ValueError, "Line 1"):
            self.read_text("not-json")

    def test_cli_writes_the_same_json_as_stdout(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "summary.json"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(main([str(ROOT / "examples/synthetic_telemetry.jsonl"), "--out", str(output)]), 0)
            self.assertEqual(json.loads(stdout.getvalue()), json.loads(output.read_text(encoding="utf-8")))

    def test_cli_rejects_overwriting_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "log.jsonl"
            original = '{"t_s": 0, "altitude_m": 0, "groundspeed_m_s": 0, "mode": "IDLE"}\n'
            path.write_text(original, encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                main([str(path), "--out", str(path)])
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
