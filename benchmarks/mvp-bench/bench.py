#!/usr/bin/env python3
"""Dependency-free runner and scoring core for MVP Bench."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import statistics
from pathlib import Path


TASKS = ("a-salon", "b-reviews", "c-quotes")
HARNESSES = ("riff", "gsd", "gstack")
REQUIRED_CHECKS = ("persistence", "research-evidence")
TASK_LABELS = {"a-salon": "예약시스템", "b-reviews": "리뷰인사이트", "c-quotes": "견적관리"}


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def protocol_hash(root: Path) -> str:
    paths = [root / "protocol.md"]
    paths += sorted((root / "tasks").rglob("*"))
    paths += sorted((root / "grader").rglob("*"))
    digest = hashlib.sha256()
    for path in paths:
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def init_pilot(root: Path, seed: str) -> dict:
    pilot = root / "pilot"
    runs_root = root / "runs"
    if pilot.exists() or runs_root.exists():
        raise FileExistsError("pilot or runs directory already exists")

    pairs = [(task, harness) for task in TASKS for harness in HARNESSES]
    random.Random(seed).shuffle(pairs)
    bundle_hash = protocol_hash(Path(__file__).parent)
    runs = []
    for index, (task, harness) in enumerate(pairs):
        run_id = "run-" + hashlib.sha256(f"{seed}:{index}".encode()).hexdigest()[:12]
        run = {"id": run_id, "task": task, "harness": harness}
        runs.append(run)
        _write_json(runs_root / run_id / "metadata.json", {
            "id": run_id,
            "task": task,
            "protocol_hash": bundle_hash,
            "execution": "anonymous-human-founder",
        })

    manifest = {"version": 1, "protocol_hash": bundle_hash, "runs": runs}
    _write_json(pilot / "assignments.json", manifest)
    return manifest


def prepare_local_results(root: Path, preflight_runs: Path | None = None) -> list[Path]:
    folders = []
    for task in TASKS:
        for harness in HARNESSES:
            folder = root / f"{TASK_LABELS[task]}_{harness}"
            if folder.exists():
                raise FileExistsError(f"result folder already exists: {folder.name}")
            folder.mkdir(parents=True)
            status = "not-run"
            execution = None
            source = preflight_runs / task if preflight_runs and harness == "riff" else None
            if source and source.is_dir():
                shutil.copytree(source, folder, dirs_exist_ok=True)
                status = "synthetic-preflight-complete"
                execution = "AI founder persona"
            _write_json(folder / "RUN.json", {
                "task": task,
                "harness": harness,
                "status": status,
                "execution": execution,
                "official_human_result": False,
            })
            if status == "not-run":
                (folder / "README.md").write_text(
                    f"# {TASK_LABELS[task]} — {harness}\n\n"
                    "아직 실행하지 않았습니다. 결과물이 생기기 전까지 비교 결과로 사용하지 않습니다.\n"
                )
            folders.append(folder)
    return folders


def grade_checks(checks: list[dict]) -> dict:
    if not isinstance(checks, list) or not checks:
        raise ValueError("checks must be a non-empty list")
    ids = []
    for check in checks:
        if set(check) != {"id", "critical", "passed", "evidence"}:
            raise ValueError("each check must contain id, critical, passed and evidence")
        if not isinstance(check["id"], str) or not check["id"]:
            raise ValueError("check id must be a non-empty string")
        if not isinstance(check["critical"], bool) or not isinstance(check["passed"], bool):
            raise ValueError("critical and passed must be booleans")
        if not isinstance(check["evidence"], str) or not check["evidence"].strip():
            raise ValueError("evidence must be a non-empty string")
        ids.append(check["id"])
    if len(ids) != len(set(ids)):
        raise ValueError("check ids must be unique")
    by_id = {check["id"]: check for check in checks}
    for required in REQUIRED_CHECKS:
        if required not in by_id:
            raise ValueError(f"missing required check: {required}")
        if not by_id[required]["critical"]:
            raise ValueError(f"required check must be critical: {required}")

    passed = sum(check["passed"] for check in checks)
    critical_failures = [check["id"] for check in checks if check["critical"] and not check["passed"]]
    pass_rate = passed / len(checks)
    return {
        "success": pass_rate >= 0.9 and not critical_failures,
        "passed": passed,
        "total": len(checks),
        "pass_rate": round(pass_rate, 4),
        "critical_failures": critical_failures,
        "checks": checks,
    }


def _file_hashes(run: Path) -> dict[str, str]:
    files = {}
    for path in sorted(run.rglob("*")):
        if path.is_symlink():
            raise ValueError("run artifacts may not contain symlinks")
        if path.is_file() and path.name != "seal.json":
            relative = path.relative_to(run).as_posix()
            files[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def _seal_digest(files: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def seal_run(run: Path) -> str:
    if (run / "seal.json").exists():
        raise FileExistsError("run is already sealed")
    files = _file_hashes(run)
    digest = _seal_digest(files)
    _write_json(run / "seal.json", {"algorithm": "sha256", "digest": digest, "files": files})
    return digest


def verify_run(run: Path) -> str:
    seal_path = run / "seal.json"
    if not seal_path.exists():
        raise FileNotFoundError("run is not sealed")
    seal = json.loads(seal_path.read_text())
    files = _file_hashes(run)
    digest = _seal_digest(files)
    if seal.get("algorithm") != "sha256" or seal.get("files") != files or seal.get("digest") != digest:
        raise ValueError("run artifacts were tampered with after sealing")
    return digest


def summarize(runs: list[dict]) -> dict:
    grouped = {}
    for harness in sorted({run["harness"] for run in runs}):
        selected = [run for run in runs if run["harness"] == harness]
        grouped[harness] = {
            "runs": len(selected),
            "successes": sum(bool(run["success"]) for run in selected),
            "median_pass_rate": statistics.median(run["pass_rate"] for run in selected),
            "median_minutes": statistics.median(run["minutes"] for run in selected),
        }
    return grouped


def _load_json(path: Path) -> object:
    return json.loads(path.read_text())


def report(root: Path) -> dict:
    assignments = _load_json(root / "pilot" / "assignments.json")
    rows = []
    for assignment in assignments["runs"]:
        run = root / "runs" / assignment["id"]
        grade = _load_json(run / "grade.json")
        timing = _load_json(run / "timing.json")
        rows.append({
            "id": assignment["id"],
            "task": assignment["task"],
            "harness": assignment["harness"],
            "success": grade["success"],
            "pass_rate": grade["pass_rate"],
            "minutes": timing["minutes"],
        })
    result = {"runs": rows, "summary": summarize(rows)}
    _write_json(root / "pilot" / "results.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="MVP Bench human-pilot runner")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init = subparsers.add_parser("init")
    init.add_argument("--root", type=Path, default=Path(__file__).parent)
    init.add_argument("--seed", required=True)
    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--root", type=Path, default=Path(__file__).parent / "local-results")
    prepare.add_argument("--with-preflight-riff", action="store_true")
    grade = subparsers.add_parser("grade")
    grade.add_argument("run", type=Path)
    seal = subparsers.add_parser("seal")
    seal.add_argument("run", type=Path)
    verify = subparsers.add_parser("verify")
    verify.add_argument("run", type=Path)
    aggregate = subparsers.add_parser("report")
    aggregate.add_argument("--root", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()

    if args.command == "init":
        value = init_pilot(args.root, args.seed)
    elif args.command == "prepare":
        source = Path(__file__).parent / "preflight" / "runs" if args.with_preflight_riff else None
        value = {"folders": [path.name for path in prepare_local_results(args.root, source)]}
    elif args.command == "grade":
        checks = _load_json(args.run / "checks.json")
        value = grade_checks(checks)
        _write_json(args.run / "grade.json", value)
    elif args.command == "seal":
        value = {"digest": seal_run(args.run)}
    elif args.command == "verify":
        value = {"digest": verify_run(args.run)}
    else:
        value = report(args.root)
    print(json.dumps(value, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
