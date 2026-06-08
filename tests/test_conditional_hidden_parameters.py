from pathlib import Path

import pytest

from openplate.cfg import project_config, template_config
from openplate.cfg.open_plate_settings import OpenPlateRuntimeSettings, defaultSettings
from openplate.project_config_resolver import resolve, resolve_parameter


pytestmark = pytest.mark.unit


def _make_template_config(parameters):
    return template_config.TemplateConfig(
        parameters,
        [],
        [],
        [],
        [],
        [],
        {},
        {},
        "{{%",
        "%}}",
        "{{{",
        "}}}",
        None,
        None,
        None,
        None,
        None,
        ".",
        [],
        []
    )


def _make_project_state(parameter_values=None):
    config_project = project_config.ProjectConfig(
        [],
        None,
        None,
        None,
        "service",
        None,
        None,
        None,
        None,
        None,
        None,
        {},
        {},
        None
    )
    config_project_template = project_config.ProjectTemplateConfig(
        "https://example.com/template.git#main",
        None,
        None,
        ".",
        None,
        parameter_values or {},
        [],
        None
    )
    return config_project, config_project_template


def test_deserialize_parameter_accepts_conditionally_hidden():
    parameter = template_config.deserialize_parameter({
        "name": "instance_type",
        "description": "Instance type",
        "default": "t3.small",
        "conditionally_hidden": "{{% if deployment_type == 'ec2' %}}true{{% else %}}false{{% endif %}}"
    })

    assert parameter.conditionally_hidden == "{{% if deployment_type == 'ec2' %}}true{{% else %}}false{{% endif %}}"


def test_deserialize_parameter_requires_default_for_conditionally_hidden():
    with pytest.raises(ValueError, match="conditionally_hidden"):
        template_config.deserialize_parameter({
            "name": "instance_type",
            "description": "Instance type",
            "conditionally_hidden": "{{% if deployment_type == 'ec2' %}}true{{% else %}}false{{% endif %}}"
        })


def test_deserialize_parameter_rejects_hidden_and_conditionally_hidden():
    with pytest.raises(ValueError, match="both hidden and conditionally_hidden"):
        template_config.deserialize_parameter({
            "name": "instance_type",
            "description": "Instance type",
            "default": "t3.small",
            "hidden": True,
            "conditionally_hidden": "{{% if deployment_type == 'ec2' %}}true{{% else %}}false{{% endif %}}"
        })


def test_deserialize_parameter_rejects_hidden_false_with_conditionally_hidden():
    with pytest.raises(ValueError, match="both hidden and conditionally_hidden"):
        template_config.deserialize_parameter({
            "name": "instance_type",
            "description": "Instance type",
            "default": "t3.small",
            "hidden": False,
            "conditionally_hidden": "{{% if deployment_type == 'ec2' %}}true{{% else %}}false{{% endif %}}"
        })


def test_resolve_conditionally_hidden_uses_earlier_parameter_answers(monkeypatch, tmp_path):
    config_template = _make_template_config([
        template_config.TemplateConfigParameter("deployment_type", "Deployment type", None, None, None),
        template_config.TemplateConfigParameter(
            "instance_type",
            "Instance type",
            "t3.small",
            None,
            None,
            "{{% if deployment_type == 'ec2' %}}true{{% else %}}false{{% endif %}}"
        ),
    ])
    config_project, config_project_template = _make_project_state()
    project_folder = tmp_path / "service"
    template_folder = tmp_path / "template"
    project_folder.mkdir()
    template_folder.mkdir()

    answers = iter(["ec2", "m5.large"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    changed = resolve(
        defaultSettings,
        OpenPlateRuntimeSettings(False, False, False, False),
        config_template,
        config_project,
        config_project_template,
        str(project_folder),
        str(template_folder),
        False
    )

    assert changed is True
    assert config_project_template.parameters["deployment_type"] == "ec2"
    assert config_project_template.parameters["instance_type"] == "m5.large"


def test_resolve_conditionally_hidden_false_uses_default_without_prompt(tmp_path):
    parameter = template_config.TemplateConfigParameter(
        "instance_type",
        "Instance type",
        "t3.small",
        None,
        None,
        "{{% if project_folder_name == 'service' %}}false{{% else %}}true{{% endif %}}"
    )
    config_template = _make_template_config([parameter])
    config_project, config_project_template = _make_project_state()
    project_folder = tmp_path / "service"
    template_folder = tmp_path / "template"
    project_folder.mkdir()
    template_folder.mkdir()

    asked, value = resolve_parameter(
        defaultSettings,
        OpenPlateRuntimeSettings(False, False, False, False),
        config_template,
        config_project,
        config_project_template,
        str(project_folder),
        str(template_folder),
        parameter,
        False,
        True
    )

    assert asked is False
    assert value == "t3.small"


def test_resolve_conditionally_hidden_respects_ask_hidden(monkeypatch, tmp_path):
    parameter = template_config.TemplateConfigParameter(
        "instance_type",
        "Instance type",
        "t3.small",
        None,
        None,
        "{{% if deployment_type == 'ec2' %}}false{{% else %}}true{{% endif %}}"
    )
    config_template = _make_template_config([parameter])
    config_project, config_project_template = _make_project_state({"deployment_type": "ec2"})
    project_folder = tmp_path / "service"
    template_folder = tmp_path / "template"
    project_folder.mkdir()
    template_folder.mkdir()

    monkeypatch.setattr("builtins.input", lambda _prompt: "m5.large")

    asked, value = resolve_parameter(
        defaultSettings,
        OpenPlateRuntimeSettings(False, True, False, False),
        config_template,
        config_project,
        config_project_template,
        str(project_folder),
        str(template_folder),
        parameter,
        False,
        False
    )

    assert asked is True
    assert value == "m5.large"


def test_resolve_conditionally_hidden_rejects_non_boolean_result(tmp_path):
    parameter = template_config.TemplateConfigParameter(
        "instance_type",
        "Instance type",
        "t3.small",
        None,
        None,
        "{{{ deployment_type }}}"
    )
    config_template = _make_template_config([parameter])
    config_project, config_project_template = _make_project_state({"deployment_type": "sometimes"})
    project_folder = tmp_path / "service"
    template_folder = tmp_path / "template"
    project_folder.mkdir()
    template_folder.mkdir()

    with pytest.raises(ValueError, match="must render to 'true' or 'false'"):
        resolve_parameter(
            defaultSettings,
            OpenPlateRuntimeSettings(False, False, False, False),
            config_template,
            config_project,
            config_project_template,
            str(project_folder),
            str(template_folder),
            parameter,
            False,
            True
        )


def test_template_docs_describe_conditionally_hidden_parameters():
    docs_text = (Path(__file__).resolve().parents[1] / "docs" / "templates.md").read_text(encoding="utf-8")

    assert "conditionally_hidden" in docs_text
    assert "If the rendered value is `false`, the parameter is treated as hidden." in docs_text
    assert "Parameters are processed in order" in docs_text