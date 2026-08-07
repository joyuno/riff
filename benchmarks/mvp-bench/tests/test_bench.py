import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "bench.py"
SPEC = importlib.util.spec_from_file_location("mvp_bench", MODULE_PATH)
bench = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bench)


class PilotHarnessTest(unittest.TestCase):
    def test_prepare_local_results_creates_nine_readable_folders(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as sources:
            source = Path(sources)
            for task in bench.TASKS:
                (source / task).mkdir()
                (source / task / "artifact.txt").write_text(task)
            folders = bench.prepare_local_results(Path(directory), source)
            self.assertEqual(9, len(folders))
            self.assertTrue((Path(directory) / "예약시스템_riff" / "artifact.txt").exists())
            self.assertEqual("not-run", json.loads((Path(directory) / "예약시스템_gsd" / "RUN.json").read_text())["status"])
            self.assertIn("아직 실행하지 않았습니다", (Path(directory) / "예약시스템_gsd" / "README.md").read_text())

    def test_protocol_hash_changes_when_protocol_bundle_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tasks").mkdir()
            (root / "grader").mkdir()
            (root / "protocol.md").write_text("v1")
            (root / "tasks" / "a.md").write_text("task")
            (root / "grader" / "schema.json").write_text("schema")
            before = bench.protocol_hash(root)
            (root / "tasks" / "a.md").write_text("changed")
            self.assertNotEqual(before, bench.protocol_hash(root))

    def test_init_creates_opaque_balanced_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = bench.init_pilot(Path(directory), "fixed-seed")
            runs = manifest["runs"]
            self.assertEqual(9, len(runs))
            self.assertEqual(9, len({run["id"] for run in runs}))
            self.assertTrue(all(run["id"].startswith("run-") for run in runs))
            self.assertTrue(all(not any(word in run["id"] for word in ("riff", "gsd", "gstack", "salon", "review", "quote")) for run in runs))
            pairs = {(run["task"], run["harness"]) for run in runs}
            self.assertEqual(9, len(pairs))
            public = json.loads((Path(directory) / "runs" / runs[0]["id"] / "metadata.json").read_text())
            self.assertNotIn("harness", public)

    def test_init_refuses_to_overwrite_existing_pilot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bench.init_pilot(root, "fixed-seed")
            with self.assertRaises(FileExistsError):
                bench.init_pilot(root, "fixed-seed")

    def test_grade_requires_threshold_and_no_critical_failure(self):
        checks = [
            {"id": f"feature-{index}", "critical": index == 0, "passed": index < 9, "evidence": "verified"}
            for index in range(10)
        ] + [
            {"id": "persistence", "critical": True, "passed": True, "evidence": "reload retained data"},
            {"id": "research-evidence", "critical": True, "passed": True, "evidence": "source linked to decision"},
        ]
        grade = bench.grade_checks(checks)
        self.assertTrue(grade["success"])
        checks[0]["passed"] = False
        self.assertFalse(bench.grade_checks(checks)["success"])

    def test_grade_requires_persistence_and_research_checks(self):
        base = [{"id": "core", "critical": True, "passed": True, "evidence": "verified"}]
        with self.assertRaisesRegex(ValueError, "persistence"):
            bench.grade_checks(base + [{"id": "research-evidence", "critical": True, "passed": True, "evidence": "verified"}])
        with self.assertRaisesRegex(ValueError, "research-evidence"):
            bench.grade_checks(base + [{"id": "persistence", "critical": True, "passed": True, "evidence": "verified"}])

    def test_grade_rejects_empty_evidence_and_duplicate_ids(self):
        checks = [
            {"id": "persistence", "critical": True, "passed": True, "evidence": ""},
            {"id": "persistence", "critical": True, "passed": True, "evidence": "duplicate"},
            {"id": "research-evidence", "critical": True, "passed": True, "evidence": "verified"},
        ]
        with self.assertRaises(ValueError):
            bench.grade_checks(checks)

    def test_seal_detects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "artifact.txt").write_text("original")
            seal = bench.seal_run(run)
            self.assertEqual(seal, bench.verify_run(run))
            (run / "artifact.txt").write_text("changed")
            with self.assertRaisesRegex(ValueError, "tampered"):
                bench.verify_run(run)

    def test_summarize_uses_medians_and_raw_counts(self):
        runs = [
            {"harness": "riff", "success": True, "pass_rate": 1.0, "minutes": 30},
            {"harness": "riff", "success": False, "pass_rate": 0.8, "minutes": 50},
            {"harness": "riff", "success": True, "pass_rate": 0.9, "minutes": 40},
        ]
        summary = bench.summarize(runs)["riff"]
        self.assertEqual(2, summary["successes"])
        self.assertEqual(3, summary["runs"])
        self.assertEqual(0.9, summary["median_pass_rate"])
        self.assertEqual(40, summary["median_minutes"])

    def test_report_joins_private_assignments_after_grading(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = bench.init_pilot(root, "fixed-seed")
            for assignment in manifest["runs"]:
                run = root / "runs" / assignment["id"]
                (run / "grade.json").write_text(json.dumps({"success": True, "pass_rate": 1.0}))
                (run / "timing.json").write_text(json.dumps({"minutes": 20}))
            result = bench.report(root)
            self.assertEqual(9, len(result["runs"]))
            self.assertEqual({"gsd", "gstack", "riff"}, set(result["summary"]))
            self.assertTrue((root / "pilot" / "results.json").exists())


if __name__ == "__main__":
    unittest.main()
