#
#              Copyright 2025 Comcast Cable Communications Management, LLC
#
#              Licensed under the Apache License, Version 2.0 (the "License");
#              you may not use this file except in compliance with the License.
#              You may obtain a copy of the License at
#
#              http://www.apache.org/licenses/LICENSE-2.0
#
#              Unless required by applicable law or agreed to in writing, software
#              distributed under the License is distributed on an "AS IS" BASIS,
#              WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#              See the License for the specific language governing permissions and
#              limitations under the License.
#
#              SPDX-License-Identifier: Apache-2.0
#
#              This product includes software developed at Comcast (https://www.comcast.com/).#
import asyncio
import json
import logging
import subprocess
from io import StringIO
from pathlib import Path

import pytest
import yaml

from openplate.__main__ import async_main
from openplate.cfg import project_config
from openplate.sources.url_source import UrlTemplateSource


pytestmark = pytest.mark.unit


def _create_git_repo(repo_path: Path):
    repo_path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    subprocess.run(["git", "config", "user.email", "tests@example.com"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    subprocess.run(["git", "config", "user.name", "OpenPlate Tests"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")


def _write_template_repo(repo_path: Path, template_yaml: str):
    repo_path.mkdir(parents=True, exist_ok=True)
    (repo_path / "openplate.template.yaml").write_text(template_yaml, encoding="utf-8")
    (repo_path / "README.md").write_text("template\n", encoding="utf-8")
    _create_git_repo(repo_path)
    return f"{repo_path.as_uri()}#main"


def _write_project_config(project_path: Path, source_url: str, dest_folder: str = "."):
    project_path.mkdir(parents=True, exist_ok=True)
    project_config_path = project_path / project_config.project_config_file_name
    project_config_path.write_text(
        yaml.safe_dump(
            {
                "templates": [
                    {
                        "src_url": source_url,
                        "dest_folder": dest_folder,
                        "parameters": {},
                    }
                ],
                "parameters": {},
                "template_file_cache": {},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_project_init_print_prompts_json_is_read_only_and_includes_conditional_sibling(tmp_path, capsys):
    repo_path = tmp_path / "template"
    source_url = _write_template_repo(
        repo_path,
        """
parameters:
  - name: service_name
    description: Service Name
  - name: include_api
    description: Include API
    default: "false"
require_sibling_templates:
  - template_url: "{{ template_src_url }}"
    dest_folder: "services/{{ project_folder_name }}/api"
    condition: "{{ include_api }}"
    parameters:
      service_name: "{{ service_name }}"
""",
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "init",
        source_url,
        "--dest-folder",
        ".",
        "--print-prompts-json",
    ]

    asyncio.run(async_main(args))

    printed = json.loads(capsys.readouterr().out)
    assert not (project_path / project_config.project_config_file_name).exists()

    root_node = next(node for node in printed if node["template"] == source_url)
    assert root_node["dest_folder"] == "."
    assert root_node["parameters"]["service_name"]["value"] is None
    assert root_node["parameters"]["service_name"]["required"] is True
    assert root_node["parameters"]["include_api"]["default"] == "false"
    assert root_node["parameters"]["include_api"]["required"] is False

    sibling_node = next(node for node in printed if node["template"] == "{{ template_src_url }}")
    assert sibling_node["dest_folder"] == "services/{{ project_folder_name }}/api"
    assert sibling_node["condition"] == "{{ include_api }}"


def test_project_init_print_prompts_json_uses_null_parameters_when_sibling_config_cannot_load(tmp_path, capsys):
    repo_path = tmp_path / "template"
    sibling_source_url = f"{repo_path.as_uri()}?path=missing#main"
    source_url = _write_template_repo(
        repo_path,
        "\n".join(
            [
                "require_sibling_templates:",
                f"  - template_url: \"{sibling_source_url}\"",
                "    dest_folder: \"broken\"",
            ]
        ),
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "init",
        source_url,
        "--dest-folder",
        ".",
        "--print-prompts-json",
    ]

    asyncio.run(async_main(args))

    printed = json.loads(capsys.readouterr().out)
    sibling_node = next(node for node in printed if node["template"] == sibling_source_url)
    assert sibling_node["parameters"] is None


def test_project_init_print_prompts_json_deduplicates_duplicate_discovered_templates(tmp_path, capsys):
    repo_path = tmp_path / "template"
    source_url = _write_template_repo(
        repo_path,
        """
require_sibling_templates:
  - template_url: "{{ template_src_url }}"
    dest_folder: "shared"
  - template_url: "{{ template_src_url }}"
    dest_folder: "shared"
""",
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "init",
        source_url,
        "--dest-folder",
        ".",
        "--print-prompts-json",
    ]

    asyncio.run(async_main(args))

    printed = json.loads(capsys.readouterr().out)
    shared_nodes = [node for node in printed if node["template"] == "{{ template_src_url }}" and node["dest_folder"] == "shared"]
    assert len(shared_nodes) == 1


def test_project_update_print_prompts_json_preserves_raw_sibling_identity_for_existing_template(tmp_path, capsys, monkeypatch):
    repo_path = tmp_path / "template"
    source_url = _write_template_repo(
        repo_path,
        """
parameters:
  - name: include_api
    description: Include API
    default: "true"
require_sibling_templates:
  - template_url: "{{ template_src_url }}"
    dest_folder: "services/{{ project_folder_name }}/api"
    condition: "{{ include_api }}"
""",
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    prompts_path = tmp_path / "prompts.json"
    prompts_path.write_text(
        json.dumps(
            [
                {
                    "template": source_url,
                    "dest_folder": ".",
                    "parameters": {
                        "include_api": {"value": "true"},
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    async def fake_walk_init(*_args, **_kwargs):
        return []

    async def fake_walk_update(*_args, **_kwargs):
        return None

    monkeypatch.setattr("openplate.walk.source_template_recursive_walk.walk_init", fake_walk_init)
    monkeypatch.setattr("openplate.walk.source_template_recursive_walk.walk_update", fake_walk_update)

    init_args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "init",
        source_url,
        "--dest-folder",
        ".",
        "--prompts-json-file",
        str(prompts_path),
    ]
    asyncio.run(async_main(init_args))
    capsys.readouterr()

    update_args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "update",
        "--print-prompts-json",
    ]
    asyncio.run(async_main(update_args))

    printed = json.loads(capsys.readouterr().out)
    sibling_nodes = [
        node for node in printed
        if node["template"] == "{{ template_src_url }}"
        and node["dest_folder"] == "services/{{ project_folder_name }}/api"
    ]

    assert len(sibling_nodes) == 1
    assert sibling_nodes[0]["condition"] == "{{ include_api }}"


def test_project_update_warns_for_ignored_templates_and_unused_parameters(tmp_path, caplog, monkeypatch):
    repo_path = tmp_path / "template"
    source_url = _write_template_repo(
        repo_path,
        """
parameters:
  - name: service_name
    description: Service Name
""",
    )
    project_path = tmp_path / "project"
    _write_project_config(project_path, source_url)

    async def fake_walk_update(*_args, **_kwargs):
        return None

    monkeypatch.setattr("openplate.walk.source_template_recursive_walk.walk_update", fake_walk_update)

    prompts_path = tmp_path / "prompts.json"
    prompts_path.write_text(
        json.dumps(
            [
                {
                    "template": source_url,
                    "dest_folder": ".",
                    "parameters": {
                        "service_name": {"value": "demo"},
                        "unused": {"value": "leftover"},
                    },
                },
                {
                    "template": "unused-template#main",
                    "dest_folder": "ignored",
                    "parameters": {},
                },
            ]
        ),
        encoding="utf-8",
    )

    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "update",
        "--prompts-json-file",
        str(prompts_path),
    ]

    with caplog.at_level(logging.WARNING):
        asyncio.run(async_main(args))

    assert any("Ignoring unused supplied prompt parameter" in record.message for record in caplog.records)
    assert any("Ignoring supplied prompt template because it was not processed" in record.message for record in caplog.records)


def test_project_init_accepts_blank_string_prompt_value(tmp_path):
    repo_path = tmp_path / "template"
    source_url = _write_template_repo(
        repo_path,
        """
parameters:
  - name: service_name
    description: Service Name
""",
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    prompts_path = tmp_path / "prompts.json"
    prompts_path.write_text(
        json.dumps(
            [
                {
                    "template": source_url,
                    "dest_folder": ".",
                    "parameters": {
                        "service_name": {"value": ""},
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "init",
        source_url,
        "--dest-folder",
        ".",
        "--prompts-json-file",
        str(prompts_path),
    ]

    asyncio.run(async_main(args))

    written_config = yaml.safe_load((project_path / project_config.project_config_file_name).read_text(encoding="utf-8"))
    assert written_config["templates"][0]["parameters"]["service_name"] == ""


def test_project_init_accepts_prompts_json_from_stdin(tmp_path, monkeypatch):
    repo_path = tmp_path / "template"
    source_url = _write_template_repo(
        repo_path,
        """
parameters:
  - name: service_name
    description: Service Name
""",
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    monkeypatch.setattr(
        "sys.stdin",
        StringIO(
            json.dumps(
                [
                    {
                        "template": source_url,
                        "dest_folder": ".",
                        "parameters": {
                            "service_name": {"value": "stdin-demo"},
                        },
                    }
                ]
            )
        ),
    )

    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "init",
        source_url,
        "--dest-folder",
        ".",
        "--prompts-json-stdin",
    ]

    asyncio.run(async_main(args))

    written_config = yaml.safe_load((project_path / project_config.project_config_file_name).read_text(encoding="utf-8"))
    assert written_config["templates"][0]["parameters"]["service_name"] == "stdin-demo"


def test_project_init_uses_default_value_in_json_mode_without_prompting(tmp_path):
    repo_path = tmp_path / "template"
    source_url = _write_template_repo(
        repo_path,
        """
parameters:
  - name: service_name
    description: Service Name
    default: demo
""",
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    prompts_path = tmp_path / "prompts.json"
    prompts_path.write_text(
        json.dumps(
            [
                {
                    "template": source_url,
                    "dest_folder": ".",
                    "parameters": None
                }
            ]
        ),
        encoding="utf-8",
    )

    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "init",
        source_url,
        "--dest-folder",
        ".",
        "--prompts-json-file",
        str(prompts_path),
    ]

    asyncio.run(async_main(args))

    written_config = yaml.safe_load((project_path / project_config.project_config_file_name).read_text(encoding="utf-8"))
    assert written_config["templates"][0]["parameters"]["service_name"] == "demo"


def test_project_init_fails_when_required_value_remains_unresolved_in_json_mode(tmp_path):
    repo_path = tmp_path / "template"
    source_url = _write_template_repo(
        repo_path,
        """
parameters:
  - name: service_name
    description: Service Name
""",
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    prompts_path = tmp_path / "prompts.json"
    prompts_path.write_text(
        json.dumps(
            [
                {
                    "template": source_url,
                    "dest_folder": ".",
                    "parameters": {
                        "service_name": {"value": None},
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "init",
        source_url,
        "--dest-folder",
        ".",
        "--prompts-json-file",
        str(prompts_path),
    ]

    with pytest.raises(Exception, match="unresolved parameter"):
        asyncio.run(async_main(args))


def test_project_init_fails_template_command_confirmation_in_json_mode(tmp_path):
    repo_path = tmp_path / "template"
    source_url = _write_template_repo(
        repo_path,
        """
init_commands:
  - command: echo setup
""",
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    prompts_path = tmp_path / "prompts.json"
    prompts_path.write_text("[]", encoding="utf-8")

    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "init",
        source_url,
        "--dest-folder",
        ".",
        "--prompts-json-file",
        str(prompts_path),
    ]

    with pytest.raises(SystemExit) as ex:
        asyncio.run(async_main(args))

    assert ex.value.code == 1


def test_project_init_print_prompts_json_reuses_single_source_fetch(tmp_path, monkeypatch, capsys):
    repo_path = tmp_path / "template"
    source_url = _write_template_repo(
        repo_path,
        """
require_sibling_templates:
  - template_url: "{{ template_src_url }}"
    dest_folder: "services/{{ project_folder_name }}/api"
""",
    )
    project_path = tmp_path / "project"
    project_path.mkdir()
    enter_count = 0
    original_enter = UrlTemplateSource.__enter__

    def counting_enter(self):
        nonlocal enter_count
        enter_count += 1
        return original_enter(self)

    monkeypatch.setattr(UrlTemplateSource, "__enter__", counting_enter)

    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-folder",
        str(project_path),
        "init",
        source_url,
        "--dest-folder",
        ".",
        "--print-prompts-json",
    ]

    asyncio.run(async_main(args))

    capsys.readouterr()
    assert enter_count == 1