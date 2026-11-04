#
# Copyright 2025 Comcast Cable Communications Management, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
#
# This product includes software developed at Comcast (https://www.comcast.com/).
#
import shutil
import subprocess
from pathlib import Path

import pytest


pytestmark = pytest.mark.unit


def _to_bash_path(path: Path) -> str:
    resolved = path.resolve()
    path_str = resolved.as_posix()
    if len(path_str) >= 3 and path_str[1] == ":" and path_str[2] == "/":
        return f"/mnt/{path_str[0].lower()}{path_str[2:]}"
    return path_str


def _run_bash_guard(script_path: Path, repo_path: Path, approved_root: Path, source_repo_root: Path):
    bash_path = shutil.which("bash")
    if bash_path is None:
        pytest.skip("bash is required for manual-test runner safety checks")

    command = (
        f"source '{_to_bash_path(script_path)}'; "
        f"assert_safe_git_repo_target '{_to_bash_path(repo_path)}' '{_to_bash_path(approved_root)}' '{_to_bash_path(source_repo_root)}'"
    )
    return subprocess.run(
        [bash_path, "-lc", command],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )


def test_manual_test_guard_accepts_target_within_disposable_root(tmp_path):
    script_path = Path("manual-tests/manual-test-lib.sh").resolve()
    source_repo_root = (tmp_path / "source-repo").resolve()
    approved_root = (tmp_path / "sandbox-root" / "manual-tests" / "work").resolve()
    repo_path = approved_root / "case-1" / "project"
    repo_path.mkdir(parents=True)
    source_repo_root.mkdir(parents=True)

    result = _run_bash_guard(script_path, repo_path, approved_root, source_repo_root)

    assert result.returncode == 0
    assert result.stderr == ""


def test_manual_test_guard_rejects_source_checkout_root(tmp_path):
    script_path = Path("manual-tests/manual-test-lib.sh").resolve()
    source_repo_root = (tmp_path / "source-repo").resolve()
    approved_root = (tmp_path / "sandbox-root" / "manual-tests" / "work").resolve()
    approved_root.mkdir(parents=True)
    source_repo_root.mkdir(parents=True)

    result = _run_bash_guard(script_path, source_repo_root, approved_root, source_repo_root)

    assert result.returncode != 0
    assert "Unsafe manual-test git target" in result.stderr


def test_manual_test_guard_rejects_target_outside_disposable_root(tmp_path):
    script_path = Path("manual-tests/manual-test-lib.sh").resolve()
    source_repo_root = (tmp_path / "source-repo").resolve()
    approved_root = (tmp_path / "sandbox-root" / "manual-tests" / "work").resolve()
    outside_repo = (tmp_path / "other-root" / "project").resolve()
    source_repo_root.mkdir(parents=True)
    approved_root.mkdir(parents=True)
    outside_repo.mkdir(parents=True)

    result = _run_bash_guard(script_path, outside_repo, approved_root, source_repo_root)

    assert result.returncode != 0
    assert "Unsafe manual-test git target outside disposable root" in result.stderr