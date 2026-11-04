#!/usr/bin/env bash
##
## Copyright 2025 Comcast Cable Communications Management, LLC
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
## http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## SPDX-License-Identifier: Apache-2.0
##
## This product includes software developed at Comcast (https://www.comcast.com/).
##

set -euo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_ROOT/manual-test-lib.sh"

usage() {
  cat <<'EOF'
Usage: ./manual-tests/cleanup-manual-tests.sh [case-1|case-2|case-3|case-4|case-5|case-6|case-7|all]
EOF
}

CASE="${1:-all}"

case "$CASE" in
  case-1|case-2|case-3|case-4|case-5|case-6|case-7|all) ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac

SOURCE_REPO_ROOT="${OPENPLATE_MANUAL_SOURCE_REPO_ROOT:-$(cd "$SCRIPT_ROOT/.." && pwd)}"
SANDBOX_RECORD_PATH="$SCRIPT_ROOT/artifacts/.sandbox-root"

remove_recorded_sandbox_if_safe() {
  if [[ ! -f "$SANDBOX_RECORD_PATH" ]]; then
    return
  fi

  local sandbox_root
  sandbox_root="$(tr -d '\r' < "$SANDBOX_RECORD_PATH")"
  if [[ -n "$sandbox_root" ]] && [[ -d "$sandbox_root" ]] && [[ "$(manual_test_path_within "$sandbox_root" "$SOURCE_REPO_ROOT")" != "1" ]]; then
    rm -rf "$sandbox_root"
  fi
  rm -f "$SANDBOX_RECORD_PATH"
}

if [[ "$CASE" == 'all' ]]; then
  cases_to_clean=(case-1 case-2 case-3 case-4 case-5 case-6 case-7)
else
  cases_to_clean=("$CASE")
fi

for root in "$SCRIPT_ROOT/work" "$SCRIPT_ROOT/artifacts"; do
  for case_id in "${cases_to_clean[@]}"; do
    rm -rf "$root/$case_id"
  done
done

remove_recorded_sandbox_if_safe

printf 'Removed generated manual-test state for: %s\n' "$(IFS=', '; echo "${cases_to_clean[*]}")"