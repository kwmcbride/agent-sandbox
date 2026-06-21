#!/usr/bin/env python3
"""Report basic statistics about the current git repository."""

from __future__ import annotations

import subprocess
import sys


def run_git(args: list[str]) -> str:
    """Run a git command and return its stdout, stripped."""
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def is_git_repo() -> bool:
    """Return True if the current directory is inside a git work tree."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0 and result.stdout.strip() == "true"


def total_commits() -> int:
    """Return the total number of commits reachable from HEAD."""
    try:
        output = run_git(["rev-list", "--count", "HEAD"])
    except subprocess.CalledProcessError:
        return 0
    return int(output) if output else 0


def unique_contributors() -> int:
    """Return the number of unique contributors by email."""
    try:
        output = run_git(["log", "--format=%ae"])
    except subprocess.CalledProcessError:
        return 0
    if not output:
        return 0
    return len({line.strip() for line in output.splitlines() if line.strip()})


def most_recently_modified_file() -> str:
    """Return the path of the file most recently changed in git history."""
    try:
        output = run_git(
            ["log", "-1", "--name-only", "--pretty=format:", "--diff-filter=AMR"]
        )
    except subprocess.CalledProcessError:
        return "(unknown)"
    for line in output.splitlines():
        path = line.strip()
        if path:
            return path
    return "(none)"


def tracked_file_count() -> int:
    """Return the number of files tracked by git."""
    try:
        output = run_git(["ls-files"])
    except subprocess.CalledProcessError:
        return 0
    if not output:
        return 0
    return sum(1 for line in output.splitlines() if line.strip())


def main() -> int:
    if not is_git_repo():
        print(
            "Error: not a git repository (or git is not installed).",
            file=sys.stderr,
        )
        return 1

    commits = total_commits()
    contributors = unique_contributors()
    recent_file = most_recently_modified_file()
    tracked = tracked_file_count()

    print("Repository statistics")
    print("---------------------")
    print(f"Total commits:            {commits}")
    print(f"Unique contributors:      {contributors}")
    print(f"Most recently modified:   {recent_file}")
    print(f"Tracked files:            {tracked}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
