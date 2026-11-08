"""Manage Django-based Amazon-style repository debugging labs."""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from lab_support.catalog import CATALOG

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "lab_support" / "base"
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.sqlite3", "*.sqlite3-*", ".venv")


def build(project, destination, case="all", clean=False):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("Destination already exists. Your changes will not be overwritten; choose a new --dest: " + str(destination))
    spec = CATALOG[project]
    shutil.copytree(BASE, destination, ignore=IGNORE)
    shutil.copytree(ROOT / "labs" / project / "reference" / "app", destination / "app", ignore=IGNORE)
    selected = [] if clean else (list(range(5)) if case == "all" else [int(case) - 1])
    for index in selected:
        item = spec["tickets"][index]
        path = destination / "app" / item["file"]
        content = path.read_text()
        if content.count(item["before"]) != 1:
            raise RuntimeError("Mutation anchor missing or ambiguous: " + item["title"])
        path.write_text(content.replace(item["before"], item["after"], 1))
    metadata = {"project": project, "case": "reference" if clean else case, "tickets": [i + 1 for i in selected]}
    (destination / "LAB.json").write_text(json.dumps(metadata, indent=2) + "\n")
    (destination / ".gitignore").write_text("__pycache__/\n*.pyc\n*.sqlite3\n*.sqlite3-*\n.venv/\n")
    reports = "\n\n".join(f'### Ticket {i + 1:02}: {spec["tickets"][i]["title"]}\n\n{spec["tickets"][i]["report"]}' for i in selected)
    task = (ROOT / "lab_support" / "TASK_TEMPLATE.md").read_text()
    replacements = {"TITLE": spec["title"], "PROVENANCE": spec["provenance"], "TICKETS": reports or "Correct reference implementation; no faults are injected.",
                    "CONTRACT": spec["contract"], "PORT": str(spec["port"]), "PROJECT": project}
    for key, value in replacements.items():
        task = task.replace("{{" + key + "}}", value)
    (destination / "TASK.md").write_text(task)
    return destination


def run(workspace, acceptance=False, project=None):
    if acceptance:
        args = [sys.executable, str(ROOT / "lab_support" / "grade.py"), str(workspace), str(ROOT / "labs" / project / "grader")]
    else:
        args = [sys.executable, "manage.py", "test", "app.tests", "--noinput", "-v", "2"]
    return subprocess.run(args, cwd=workspace, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def selfcheck(projects):
    with tempfile.TemporaryDirectory() as temporary:
        for project in projects:
            spec = CATALOG[project]
            reference = build(project, Path(temporary) / (project + "-ref"), clean=True)
            for acceptance in (False, True):
                result = run(reference, acceptance, project)
                if result.returncode:
                    print(result.stdout)
                    return 1
            print(f"{project}: reference smoke + acceptance PASS", flush=True)
            for case in ["01", "02", "03", "04", "05", "all"]:
                workspace = build(project, Path(temporary) / (project + "-" + case), case)
                smoke = run(workspace)
                result = run(workspace, True, project)
                actual = set(re.findall(r"^(?:FAIL|ERROR): (test_\w+)", result.stdout, re.MULTILINE))
                expected = {item["test"] for item in spec["tickets"]} if case == "all" else {spec["tickets"][int(case) - 1]["test"]}
                ok = smoke.returncode == 0 and result.returncode != 0 and actual == expected
                print(f"{project}/{case}: {'PASS' if ok else 'FAIL'}; smoke={smoke.returncode == 0}; expected={len(expected)} observed={len(actual)}", flush=True)
                if not ok:
                    print(smoke.stdout, result.stdout)
                    return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    for command in ("new", "reference"):
        sub = commands.add_parser(command)
        sub.add_argument("project", choices=CATALOG)
        sub.add_argument("--dest", type=Path)
        if command == "new":
            sub.add_argument("--case", choices=["01", "02", "03", "04", "05", "all"], default="all")
    grade = commands.add_parser("grade")
    grade.add_argument("workspace", type=Path)
    check = commands.add_parser("selfcheck")
    check.add_argument("project", choices=list(CATALOG) + ["all"], default="all", nargs="?")
    args = parser.parse_args()
    if args.command == "list":
        for project, spec in CATALOG.items():
            print(project + ": " + spec["title"] + " · 5 tickets")
    elif args.command in ("new", "reference"):
        case = getattr(args, "case", "all")
        destination = args.dest or ROOT / "runs" / (args.project + "-" + ("reference" if args.command == "reference" else case))
        try:
            print(build(args.project, destination, case, args.command == "reference"))
        except ValueError as error:
            parser.error(str(error))
    elif args.command == "grade":
        workspace = args.workspace.resolve()
        metadata = workspace / "LAB.json"
        if not metadata.is_file():
            parser.error("Workspace must contain LAB.json")
        project = json.loads(metadata.read_text()).get("project")
        if project not in CATALOG:
            parser.error("Unknown project")
        result = run(workspace, True, project)
        print(result.stdout, end="")
        return result.returncode
    else:
        return selfcheck(list(CATALOG) if args.project == "all" else [args.project])
    return 0


if __name__ == "__main__":
    sys.exit(main())
