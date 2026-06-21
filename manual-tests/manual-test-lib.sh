#!/usr/bin/env bash

manual_test_python_exe() {
  if [[ -n "${PYTHON_EXE:-}" ]]; then
    printf '%s\n' "$PYTHON_EXE"
  elif command -v python.exe >/dev/null 2>&1; then
    printf 'python.exe\n'
  elif command -v py.exe >/dev/null 2>&1; then
    printf 'py.exe\n'
  elif command -v python3 >/dev/null 2>&1; then
    printf 'python3\n'
  elif command -v python >/dev/null 2>&1; then
    printf 'python\n'
  elif command -v py >/dev/null 2>&1; then
    printf 'py\n'
  else
    echo "No Python launcher found in PATH for bash. Set PYTHON_EXE explicitly." >&2
    return 1
  fi
}

manual_test_canonical_path() {
  local python_exe
  python_exe="$(manual_test_python_exe)" || return 1
  "$python_exe" - "$1" <<'PY' | tr -d '\r'
from pathlib import Path
import re
import sys

raw_path = sys.argv[1].replace('\\', '/')
match = re.match(r'^/mnt/([a-zA-Z])/(.*)$', raw_path)
if match:
    drive = match.group(1).upper() + ':'
    rest = '\\' + match.group(2).replace('/', '\\')
    raw_path = drive + rest

print(Path(raw_path).resolve())
PY
}

manual_test_path_within() {
  local python_exe
  python_exe="$(manual_test_python_exe)" || return 1
  "$python_exe" - "$1" "$2" <<'PY' | tr -d '\r'
from pathlib import Path
import os
import re
import sys

def normalize(raw_path: str) -> str:
  raw_path = raw_path.replace('\\', '/')
  match = re.match(r'^/mnt/([a-zA-Z])/(.*)$', raw_path)
  if match:
    drive = match.group(1).upper() + ':'
    rest = '\\' + match.group(2).replace('/', '\\')
    return drive + rest
  return raw_path

child = str(Path(normalize(sys.argv[1])).resolve())
parent = str(Path(normalize(sys.argv[2])).resolve())

try:
    print("1" if os.path.commonpath([child, parent]) == parent else "0")
except ValueError:
    print("0")
PY
}

assert_safe_git_repo_target() {
  local repo_path="$1"
  local approved_root="$2"
  local source_repo_root="$3"
  local resolved_repo_path
  local resolved_approved_root
  local resolved_source_repo_root

  resolved_repo_path="$(manual_test_canonical_path "$repo_path")" || return 1
  resolved_approved_root="$(manual_test_canonical_path "$approved_root")" || return 1
  resolved_source_repo_root="$(manual_test_canonical_path "$source_repo_root")" || return 1

  if [[ "$(manual_test_path_within "$resolved_repo_path" "$resolved_approved_root")" != "1" ]]; then
    echo "Unsafe manual-test git target outside disposable root: $resolved_repo_path" >&2
    return 1
  fi

  if [[ "$(manual_test_path_within "$resolved_repo_path" "$resolved_source_repo_root")" == "1" ]]; then
    echo "Unsafe manual-test git target inside source checkout: $resolved_repo_path" >&2
    return 1
  fi
}