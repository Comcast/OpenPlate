import asyncio
import json
import subprocess
import textwrap
from pathlib import Path

import pytest
import yaml

from openplate.__main__ import async_main
from openplate.cfg import template_config
from openplate.cfg.open_plate_settings import OpenPlateRuntimeSettings, defaultSettings
from openplate.cfg.project_config import ProjectConfig, ProjectTemplateConfig
from openplate.project_config_resolver import resolve_parameter_hidden_state
from openplate.walk.source_template_recursive_walk import VerifyWalkOptions, source_template_recursive_walk_all


pytestmark = pytest.mark.unit


def _create_git_repo(repo_path: Path):
    repo_path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    subprocess.run(["git", "config", "user.email", "tests@example.com"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    subprocess.run(["git", "config", "user.name", "OpenPlate Tests"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")


def _write_template_repo(repo_path: Path, template_yaml: str, files: dict[str, str] | None = None) -> str:
    repo_path.mkdir(parents=True, exist_ok=True)
    normalized_template_yaml = textwrap.dedent(template_yaml).lstrip()
    if "ignore_paths:" not in normalized_template_yaml:
        normalized_template_yaml = (
            "ignore_paths:\n"
            "  - '^openplate\\.template\\.yaml$'\n"
            + normalized_template_yaml
        )
    (repo_path / "openplate.template.yaml").write_text(normalized_template_yaml, encoding="utf-8")

    for relative_path, contents in (files or {}).items():
        file_path = repo_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(contents, encoding="utf-8")

    _create_git_repo(repo_path)
    return f"{repo_path.as_uri()}#main"


def _run_init(tmp_path: Path, project_path: Path, source_url: str, extra_args: list[str] | None = None):
    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-root",
        str(project_path),
        "init",
        source_url,
    ]
    if extra_args:
        args.extend(extra_args)
    asyncio.run(async_main(args))


def _project_config_with_templates(*templates: ProjectTemplateConfig) -> ProjectConfig:
    return ProjectConfig(
        list(templates),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        {},
        {},
        None,
    )


def test_template_config_deserializes_imports_and_exports():
    config = template_config.deserialize_project_config(
        {
            "parameters": [],
            "imports": [
                {
                    "export-key": "worker-name",
                    "location": "services/api",
                    "import-key": "worker_name",
                }
            ],
            "exports": [
                {
                    "key": "deployable-projects",
                    "value": "services/api:dotnet10-api",
                    "location": ".",
                    "shared-export": True,
                }
            ],
        }
    )

    assert len(config.imports) == 1
    assert config.imports[0].export_key == "worker-name"
    assert config.imports[0].location == "services/api"
    assert config.imports[0].import_key == "worker_name"

    assert len(config.exports) == 1
    assert config.exports[0].key == "deployable-projects"
    assert config.exports[0].value == "services/api:dotnet10-api"
    assert config.exports[0].location == "."
    assert config.exports[0].shared_export is True


def test_template_config_omitted_import_and_export_locations_stay_unset():
    config = template_config.deserialize_project_config(
        {
            "parameters": [],
            "imports": [{"export-key": "worker-name", "import-key": "worker_name"}],
            "exports": [{"key": "worker-name", "value": "api-worker"}],
        }
    )

    assert config.imports[0].location is None
    assert config.exports[0].location is None
    assert config.exports[0].shared_export is False


def test_template_config_rejects_missing_import_fields():
    with pytest.raises(ValueError, match="export-key is required in imports entry"):
        template_config.deserialize_project_config({"parameters": [], "imports": [{"import-key": "worker_name"}]})

    with pytest.raises(ValueError, match="import-key is required in imports entry"):
        template_config.deserialize_project_config({"parameters": [], "imports": [{"export-key": "worker-name"}]})


def test_template_config_rejects_missing_export_fields():
    with pytest.raises(ValueError, match="key is required in exports entry"):
        template_config.deserialize_project_config({"parameters": [], "exports": [{"value": "api-worker"}]})

    with pytest.raises(ValueError, match="value is required in exports entry"):
        template_config.deserialize_project_config({"parameters": [], "exports": [{"key": "worker-name"}]})


def test_template_config_rejects_non_boolean_shared_export():
    with pytest.raises(TypeError, match="shared-export in template configuration is not a boolean"):
        template_config.deserialize_project_config(
            {
                "parameters": [],
                "exports": [{"key": "worker-name", "value": "api-worker", "shared-export": "true"}],
            }
        )


def test_init_resolves_import_from_direct_sibling(tmp_path):
    worker_source_url = _write_template_repo(
        tmp_path / "worker-template",
        """
        exports:
          - key: "worker-name"
            value: "api-worker"
        """,
    )
    root_source_url = _write_template_repo(
        tmp_path / "root-template",
        f"""
        replacement_paths:
          - "generated/.*"
        require_sibling_templates:
          - template_url: "{worker_source_url}"
            dest_folder: "workers/common"
        imports:
          - export-key: "worker-name"
            location: "workers/common"
            import-key: "worker_name"
        """,
        {"generated/info.txt": "{{ imports.worker_name }}\n"},
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    _run_init(tmp_path, project_path, root_source_url)

    assert (project_path / "generated" / "info.txt").read_text(encoding="utf-8") == "api-worker\n"


def test_init_resolves_import_from_recursive_sibling_tree(tmp_path):
    leaf_source_url = _write_template_repo(
        tmp_path / "leaf-template",
        """
        exports:
          - key: "artifact-name"
            value: "nested-worker"
        """,
    )
    middle_source_url = _write_template_repo(
        tmp_path / "middle-template",
        f"""
        require_sibling_templates:
          - template_url: "{leaf_source_url}"
            dest_folder: "leaf"
        """,
    )
    root_source_url = _write_template_repo(
        tmp_path / "root-template",
        f"""
        replacement_paths:
          - "generated/.*"
        require_sibling_templates:
          - template_url: "{middle_source_url}"
            dest_folder: "middle"
        imports:
          - export-key: "artifact-name"
            location: "leaf"
            import-key: "artifact_name"
        """,
        {"generated/info.txt": "{{ imports.artifact_name }}\n"},
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    _run_init(tmp_path, project_path, root_source_url)

    assert (project_path / "generated" / "info.txt").read_text(encoding="utf-8") == "nested-worker\n"


def test_recursive_walk_does_not_resolve_import_from_unrelated_earlier_export(tmp_path):
    unrelated_source_url = _write_template_repo(
        tmp_path / "unrelated-template",
        """
        exports:
          - key: "worker-name"
            value: "unrelated"
        """,
    )
    consumer_source_url = _write_template_repo(
        tmp_path / "consumer-template",
        """
        imports:
          - export-key: "worker-name"
            import-key: "worker_name"
        """,
    )
    project_path = tmp_path / "project"
    project_path.mkdir()
    config_project = _project_config_with_templates(
        ProjectTemplateConfig(unrelated_source_url, None, None, ".", None, {}, [], False),
        ProjectTemplateConfig(consumer_source_url, None, None, ".", None, {}, [], False),
    )

    with pytest.raises(RuntimeError, match="Unresolved import"):
        asyncio.run(
            source_template_recursive_walk_all(
                defaultSettings,
                OpenPlateRuntimeSettings(False, False, True, True),
                str(project_path),
                VerifyWalkOptions(False, False),
                config_project,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
            )
        )


def test_init_reuses_completed_exports_for_repeated_sibling_instance(tmp_path):
    common_worker_source_url = _write_template_repo(
        tmp_path / "common-worker-template",
        """
        exports:
          - key: "worker-name"
            value: "common-worker"
        """,
    )
    service_a_source_url = _write_template_repo(
        tmp_path / "service-a-template",
        f"""
        replacement_paths:
          - "generated/a.txt"
        require_sibling_templates:
          - template_url: "{common_worker_source_url}"
            dest_folder: "workers/common"
        imports:
          - export-key: "worker-name"
            location: "workers/common"
            import-key: "worker_name"
        """,
        {"generated/a.txt": "{{ imports.worker_name }}\n"},
    )
    service_b_source_url = _write_template_repo(
        tmp_path / "service-b-template",
        f"""
        replacement_paths:
          - "generated/b.txt"
        require_sibling_templates:
          - template_url: "{common_worker_source_url}"
            dest_folder: "workers/common"
        imports:
          - export-key: "worker-name"
            location: "workers/common"
            import-key: "worker_name"
        """,
        {"generated/b.txt": "{{ imports.worker_name }}\n"},
    )
    root_source_url = _write_template_repo(
        tmp_path / "root-template",
        f"""
        require_sibling_templates:
          - template_url: "{service_a_source_url}"
            dest_folder: "service-a"
          - template_url: "{service_b_source_url}"
            dest_folder: "service-b"
        """,
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    _run_init(tmp_path, project_path, root_source_url)

    assert (project_path / "generated" / "a.txt").read_text(encoding="utf-8") == "common-worker\n"
    assert (project_path / "generated" / "b.txt").read_text(encoding="utf-8") == "common-worker\n"

    written_config = yaml.safe_load((project_path / ".openplate.project.yaml").read_text(encoding="utf-8"))
    worker_entries = [
        template
        for template in written_config["templates"]
        if template["src_url"] == common_worker_source_url and template["dest_folder"] == "workers/common"
    ]
    assert len(worker_entries) == 1


def test_init_registers_exports_after_init_commands_complete(tmp_path):
    worker_source_url = _write_template_repo(
        tmp_path / "worker-template",
        """
        config_files:
          runtime_data: "generated/runtime.yaml"
        init_commands:
          - command: >-
              python -c "from pathlib import Path; Path('generated').mkdir(exist_ok=True); Path('generated/runtime.yaml').write_text('name: post-init\\n', encoding='utf-8')"
        exports:
          - key: "runtime-name"
            value: "{{ runtime_data.name }}"
        """,
    )
    root_source_url = _write_template_repo(
        tmp_path / "root-template",
        f"""
        replacement_paths:
          - "generated/.*"
        require_sibling_templates:
          - template_url: "{worker_source_url}"
            dest_folder: "."
        imports:
          - export-key: "runtime-name"
            import-key: "runtime_name"
        """,
        {"generated/info.txt": "{{ imports.runtime_name }}\n"},
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    _run_init(tmp_path, project_path, root_source_url, ["--allow-template-commands"])

    assert (project_path / "generated" / "info.txt").read_text(encoding="utf-8") == "post-init\n"


def test_recursive_walk_rejects_duplicate_non_shared_exports(tmp_path):
    exporter_one_source_url = _write_template_repo(
        tmp_path / "exporter-one-template",
        """
        exports:
          - key: "worker-name"
            value: "one"
        """,
    )
    exporter_two_source_url = _write_template_repo(
        tmp_path / "exporter-two-template",
        """
        exports:
          - key: "worker-name"
            value: "two"
        """,
    )
    project_path = tmp_path / "project"
    project_path.mkdir()
    config_project = _project_config_with_templates(
        ProjectTemplateConfig(exporter_one_source_url, None, None, ".", None, {}, [], False),
        ProjectTemplateConfig(exporter_two_source_url, None, None, ".", None, {}, [], False),
    )

    with pytest.raises(RuntimeError, match="Duplicate export"):
        asyncio.run(
            source_template_recursive_walk_all(
                defaultSettings,
                OpenPlateRuntimeSettings(False, False, True, True),
                str(project_path),
                VerifyWalkOptions(False, False),
                config_project,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
            )
        )


def test_init_imports_shared_exports_as_list(tmp_path):
    exporter_one_source_url = _write_template_repo(
        tmp_path / "exporter-one-template",
        """
        exports:
          - key: "deployable-projects"
            value: "one"
            shared-export: true
        """,
    )
    exporter_two_source_url = _write_template_repo(
        tmp_path / "exporter-two-template",
        """
        exports:
          - key: "deployable-projects"
            value: "two"
            shared-export: true
        """,
    )
    root_source_url = _write_template_repo(
        tmp_path / "root-template",
        f"""
        replacement_paths:
          - "generated/.*"
        require_sibling_templates:
          - template_url: "{exporter_one_source_url}"
            dest_folder: "."
          - template_url: "{exporter_two_source_url}"
            dest_folder: "."
        imports:
          - export-key: "deployable-projects"
            import-key: "deployable_projects"
        """,
        {"generated/list.txt": "{{ imports.deployable_projects | join: ',' }}\n"},
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    _run_init(tmp_path, project_path, root_source_url)

    assert (project_path / "generated" / "list.txt").read_text(encoding="utf-8") == "one,two\n"


def test_imports_are_not_available_in_parameter_defaults(tmp_path):
    worker_source_url = _write_template_repo(
        tmp_path / "worker-template",
        """
        exports:
          - key: "worker-name"
            value: "api-worker"
        """,
    )
    root_source_url = _write_template_repo(
        tmp_path / "root-template",
        f"""
        replacement_paths:
          - "generated/.*"
        parameters:
          - name: imported_default
            description: Imported default
            default: "{{{{ imports.worker_name }}}}"
            hidden: true
        require_sibling_templates:
          - template_url: "{worker_source_url}"
            dest_folder: "."
        imports:
          - export-key: "worker-name"
            import-key: "worker_name"
        """,
        {"generated/info.txt": "parameter={{ imported_default }}|import={{ imports.worker_name }}\n"},
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    _run_init(tmp_path, project_path, root_source_url)

    assert (project_path / "generated" / "info.txt").read_text(encoding="utf-8") == "parameter=|import=api-worker\n"


def test_imports_are_not_available_in_conditionally_hidden(tmp_path):
    config_template = template_config.deserialize_project_config(
        {
            "parameters": [
                {
                    "name": "conditional_param",
                    "description": "Conditional Param",
                    "default": "hidden-default",
                    "conditionally_hidden": "{% if imports.worker_name == 'api-worker' %}true{% else %}false{% endif %}",
                }
            ]
        }
    )
    config_project_template = ProjectTemplateConfig(
        "https://example.com/template#main",
        None,
        None,
        ".",
        None,
        {},
        [],
        False,
    )
    config_project = _project_config_with_templates(config_project_template)

    is_hidden = resolve_parameter_hidden_state(
        config_template,
        config_project,
        config_project_template,
        str(tmp_path),
        str(tmp_path),
        config_template.parameters[0],
        OpenPlateRuntimeSettings(False, False, True, True),
    )

    assert is_hidden is True


def test_imports_are_not_available_in_sibling_dest_folder_rendering(tmp_path):
    worker_source_url = _write_template_repo(
        tmp_path / "worker-template",
        """
        exports:
          - key: "worker-name"
            value: "api-worker"
        """,
    )
    child_source_url = _write_template_repo(
        tmp_path / "child-template",
        """
        exports:
          - key: "child"
            value: "child"
        """,
    )
    root_source_url = _write_template_repo(
        tmp_path / "root-template",
        f"""
        require_sibling_templates:
          - template_url: "{worker_source_url}"
            dest_folder: "worker"
          - template_url: "{child_source_url}"
            dest_folder: "child/{{{{ imports.worker_name }}}}"
        """,
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    _run_init(tmp_path, project_path, root_source_url)

    written_config = yaml.safe_load((project_path / ".openplate.project.yaml").read_text(encoding="utf-8"))
    child_entry = next(template for template in written_config["templates"] if template["src_url"] == child_source_url)
    assert child_entry["dest_folder"] == "child"


def test_imports_are_not_available_in_sibling_condition_rendering(tmp_path):
    worker_source_url = _write_template_repo(
        tmp_path / "worker-template",
        """
        exports:
          - key: "worker-name"
            value: "api-worker"
        """,
    )
    child_source_url = _write_template_repo(
        tmp_path / "child-template",
        """
        exports:
          - key: "child"
            value: "child"
        """,
    )
    root_source_url = _write_template_repo(
        tmp_path / "root-template",
        f"""
        require_sibling_templates:
          - template_url: "{worker_source_url}"
            dest_folder: "worker"
          - template_url: "{child_source_url}"
            dest_folder: "child"
            condition: "{{% if imports.worker_name == 'api-worker' %}}true{{% else %}}false{{% endif %}}"
        """,
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    _run_init(tmp_path, project_path, root_source_url)

    written_config = yaml.safe_load((project_path / ".openplate.project.yaml").read_text(encoding="utf-8"))
    child_entries = [template for template in written_config["templates"] if template["src_url"] == child_source_url]
    assert child_entries == []


def test_imports_are_not_available_in_prompt_json_export(tmp_path, capsys):
    worker_source_url = _write_template_repo(
        tmp_path / "worker-template",
        """
        exports:
          - key: "worker-name"
            value: "api-worker"
        """,
    )
    root_source_url = _write_template_repo(
        tmp_path / "root-template",
        f"""
        parameters:
          - name: imported_default
            description: Imported default
            default: "{{{{ imports.worker_name }}}}"
        require_sibling_templates:
          - template_url: "{worker_source_url}"
            dest_folder: "."
        imports:
          - export-key: "worker-name"
            import-key: "worker_name"
        """,
    )
    project_path = tmp_path / "project"
    project_path.mkdir()

    args = [
        "openplate",
        "-c",
        str(tmp_path / "missing-config.yaml"),
        "project",
        "--project-root",
        str(project_path),
        "print-init-json",
        root_source_url,
        "--verbose",
    ]

    asyncio.run(async_main(args))

    printed = json.loads(capsys.readouterr().out)
    root_node = next(node for node in printed if node["info"]["template"] == root_source_url)
    assert root_node["info"]["parameters"]["imported_default"]["default"] == ""


def test_recursive_walk_rejects_mixed_shared_and_non_shared_exports(tmp_path):
    exporter_one_source_url = _write_template_repo(
        tmp_path / "exporter-one-template",
        """
        exports:
          - key: "deployable-projects"
            value: "one"
            shared-export: true
        """,
    )
    exporter_two_source_url = _write_template_repo(
        tmp_path / "exporter-two-template",
        """
        exports:
          - key: "deployable-projects"
            value: "two"
        """,
    )
    project_path = tmp_path / "project"
    project_path.mkdir()
    config_project = _project_config_with_templates(
        ProjectTemplateConfig(exporter_one_source_url, None, None, ".", None, {}, [], False),
        ProjectTemplateConfig(exporter_two_source_url, None, None, ".", None, {}, [], False),
    )

    with pytest.raises(RuntimeError, match="Cannot mix shared and non-shared exports"):
        asyncio.run(
            source_template_recursive_walk_all(
                defaultSettings,
                OpenPlateRuntimeSettings(False, False, True, True),
                str(project_path),
                VerifyWalkOptions(False, False),
                config_project,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
            )
        )
