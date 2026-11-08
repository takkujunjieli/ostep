"""Create independent practice repositories and run instructor checks."""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Instructor-only mutation catalog. Candidates start inside their own workspace.
CASES = {
    "01": {
        "title": "The last available item cannot be purchased",
        "report": "BOOK shows stock 10. Buying 9 succeeds, but buying 10 returns insufficient stock. Allow an exact-stock purchase while continuing to reject requests above available stock.",
        "before": 'if product["stock"] < quantity:',
        "after": 'if product["stock"] <= quantity:',
        "failures": {"test_01_exact_stock_is_allowed"},
    },
    "02": {
        "title": "Requests from different customers return the same order",
        "report": "Two customers use the same client-generated request_key. The second receives the first customer order. Scope retries to each customer while ensuring that same-customer retries deduct stock only once.",
        "before": '"SELECT * FROM orders WHERE customer_id = ? AND request_key = ?",\n                (customer_id, request_key),',
        "after": '"SELECT * FROM orders WHERE request_key = ?",\n                (request_key,),',
        "failures": {"test_02_idempotency_keys_are_customer_scoped"},
    },
    "03": {
        "title": "Discounted totals are occasionally one cent too low",
        "report": "PEN costs 101 cents. A 50 percent discount should yield 51 cents, and three pens should total 152 cents. Round once after discounting the entire order subtotal.",
        "before": 'return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))',
        "after": 'return int(amount)',
        "failures": {"test_03_half_cent_rounds_up", "test_discount_rounds_once_for_entire_order"},
    },
    "04": {
        "title": "Time-zone filters miss orders",
        "report": "An order created at 2026-10-24T12:00:00Z is missing from a search between 07:59:59-04:00 and 08:00:01-04:00. Interpret timezone-aware timestamps on the same absolute timeline.",
        "before": 'return parsed.astimezone(timezone.utc)',
        "after": 'return parsed.replace(tzinfo=timezone.utc)',
        "failures": {"test_04_equivalent_offset_matches_utc", "test_time_offsets_cross_calendar_day"},
    },
    "05": {
        "title": "Pagination repeats orders",
        "report": "Create five orders and fetch two per page using next_cursor. Some orders repeat. Return each order exactly once and use null for next_cursor on the final page.",
        "before": 'AND id > ? ORDER BY id LIMIT ?',
        "after": 'AND id >= ? ORDER BY id LIMIT ?',
        "failures": {"test_05_pagination_never_repeats_boundary"},
    },
    "06": {
        "title": "Failed orders still reduce stock",
        "report": "A cart containing BOOK and unknown SKU ZZZ returns UNKNOWN_SKU but reduces BOOK stock. A later out-of-stock item causes a similar problem. Failed orders must leave both stock and orders unchanged.",
        "before": 'connection.rollback()',
        "after": 'connection.commit()',
        "failures": {"test_06_failed_order_rolls_back_earlier_stock_update", "test_insufficient_later_item_rolls_back"},
    },
}


def create_workspace(case, destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("Destination already exists; choose another --dest: " + str(destination))
    selected = list(CASES) if case == "all" else [case]
    destination.mkdir(parents=True)
    shutil.copytree(ROOT / "shop", destination / "shop", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "tests", destination / "tests", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(ROOT / ".gitignore", destination / ".gitignore")
    source_file = destination / "shop" / "service.py"
    source = source_file.read_text()
    for key in selected:
        case_info = CASES[key]
        if source.count(case_info["before"]) != 1:
            raise RuntimeError("Mutation anchor must occur exactly once: " + key)
        source = source.replace(case_info["before"], case_info["after"], 1)
    source_file.write_text(source)
    tickets = "\n\n".join("### Ticket " + key + ": " + CASES[key]["title"] + "\n\n" + CASES[key]["report"]
                            for key in selected)
    task = (ROOT / "docs" / "CANDIDATE.md").read_text().replace("{{TICKETS}}", tickets)
    (destination / "TASK.md").write_text(task)
    return destination


def run_suite(workspace, instructor=False):
    suite = ROOT / "grader" if instructor else Path(workspace) / "tests"
    return subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(suite), "-v"],
                          cwd=str(workspace), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def selfcheck():
    reference = run_suite(ROOT, True)
    print("reference regression:", "PASS" if reference.returncode == 0 else "FAIL")
    if reference.returncode:
        print(reference.stdout)
        return 1
    with tempfile.TemporaryDirectory() as temporary:
        for key in list(CASES) + ["all"]:
            workspace = create_workspace(key, Path(temporary) / key)
            smoke = run_suite(workspace)
            regression = run_suite(workspace, True)
            observed = set(re.findall(r"^(?:FAIL|ERROR): (test_\w+)", regression.stdout, re.MULTILINE))
            expected = set().union(*(case["failures"] for case in CASES.values())) if key == "all" else CASES[key]["failures"]
            ok = smoke.returncode == 0 and regression.returncode != 0 and observed == expected
            print("scenario %s: %s; smoke=%s, expected failures=%d, observed=%d" % (
                key, "PASS" if ok else "FAIL", smoke.returncode == 0, len(expected), len(observed)))
            if not ok:
                print(smoke.stdout, regression.stdout)
                return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("new", help="Create a fresh buggy practice workspace")
    new.add_argument("case", choices=list(CASES) + ["all"])
    new.add_argument("--dest", type=Path)
    grade = commands.add_parser("grade", help="Run instructor acceptance tests against a workspace")
    grade.add_argument("workspace", type=Path)
    commands.add_parser("selfcheck", help="Verify reference and every intentional bug")
    args = parser.parse_args()
    if args.command == "new":
        try:
            print(create_workspace(args.case, args.dest or ROOT / "runs" / args.case))
        except ValueError as error:
            parser.error(str(error))
    elif args.command == "grade":
        workspace = args.workspace.resolve()
        if not (workspace / "shop" / "service.py").is_file():
            parser.error("Not an order-service workspace: " + str(workspace))
        result = run_suite(workspace, True)
        print(result.stdout, end="")
        return result.returncode
    else:
        return selfcheck()
    return 0


if __name__ == "__main__":
    sys.exit(main())
