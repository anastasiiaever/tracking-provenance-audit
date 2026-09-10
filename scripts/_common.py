"""Shared helpers for the verification scripts. No scientific logic lives here."""
from __future__ import annotations

import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(ROOT, "src") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "src"))


def path(*parts):
    return os.path.join(ROOT, *parts)


def read_csv(*parts):
    with open(path(*parts), newline="") as f:
        return list(csv.DictReader(f))


def read_json(*parts):
    with open(path(*parts)) as f:
        return json.load(f)


class Checks:
    """Collects pass/fail checks and prints a stable report."""

    def __init__(self, title):
        self.title = title
        self.rows = []

    def check(self, name, ok, detail=""):
        self.rows.append((name, bool(ok), detail))
        return ok

    def equal(self, name, got, want, tol=None):
        if tol is None:
            ok = got == want
        else:
            ok = abs(float(got) - float(want)) <= tol
        return self.check(name, ok, f"got {got!r}, expected {want!r}")

    def report(self):
        width = max(len(n) for n, _, _ in self.rows) + 2
        print(f"\n{self.title}")
        print("=" * len(self.title))
        for name, ok, detail in self.rows:
            mark = "PASS" if ok else "FAIL"
            line = f"  [{mark}] {name.ljust(width)}"
            if not ok and detail:
                line += detail
            print(line)
        failed = [n for n, ok, _ in self.rows if not ok]
        print(f"  -- {len(self.rows) - len(failed)}/{len(self.rows)} checks passed")
        return failed
