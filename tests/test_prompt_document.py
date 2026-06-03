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
import pytest

from openplate.prompts.prompt_document import PromptDocument, PromptInputTracker


pytestmark = pytest.mark.unit


def test_prompt_document_rejects_duplicate_template_entries():
    json_string = """
    [
      {"template": "repo#main", "dest_folder": ".", "parameters": {}},
      {"template": "repo#main", "dest_folder": ".", "parameters": {}}
    ]
    """

    with pytest.raises(ValueError, match="Duplicate prompt template entry"):
        PromptDocument.from_json_string(json_string)


def test_prompt_document_rejects_missing_parameter_value_field():
    json_string = """
    [
      {
        "template": "repo#main",
        "dest_folder": ".",
        "parameters": {
          "service_name": {
            "default": "demo"
          }
        }
      }
    ]
    """

    with pytest.raises(ValueError, match="must include a 'value' field"):
        PromptDocument.from_json_string(json_string)


def test_prompt_document_rejects_non_string_parameter_value():
    json_string = """
    [
      {
        "template": "repo#main",
        "dest_folder": ".",
        "parameters": {
          "service_name": {
            "value": 123
          }
        }
      }
    ]
    """

    with pytest.raises(TypeError, match="'value' must be a string or null"):
        PromptDocument.from_json_string(json_string)


def test_prompt_document_rejects_non_boolean_hidden_flag():
    json_string = """
    [
      {
        "template": "repo#main",
        "dest_folder": ".",
        "parameters": {
          "service_name": {
            "value": null,
            "hidden": "yes"
          }
        }
      }
    ]
    """

    with pytest.raises(TypeError, match="'hidden' must be a boolean or null"):
        PromptDocument.from_json_string(json_string)


def test_prompt_document_round_trips_null_parameters():
    json_string = """
    [
      {
        "template": "repo#main",
        "dest_folder": ".",
        "condition": "{{ include_api }}",
        "parameters": null
      }
    ]
    """

    document = PromptDocument.from_json_string(json_string)

    assert document.templates[0].parameters is None
    assert '"parameters": null' in document.to_json_string()


def test_prompt_input_tracker_treats_null_parameters_as_no_supplied_values():
    tracker = PromptInputTracker.from_json_string(
        """
        [
          {
            "template": "repo#main",
            "dest_folder": ".",
            "parameters": null
          }
        ]
        """
    )

    value, found = tracker.get_parameter_value("repo#main", ".", "service_name")

    assert value is None
    assert found is False


def test_prompt_input_tracker_reports_unused_supplied_parameters():
    tracker = PromptInputTracker.from_json_string(
        """
        [
          {
            "template": "repo#main",
            "dest_folder": ".",
            "parameters": {
              "used": {"value": "x"},
              "unused": {"value": "y"},
              "null_value": {"value": null}
            }
          }
        ]
        """
    )

    value, found = tracker.get_parameter_value("repo#main", ".", "used")

    assert value == "x"
    assert found is True
    assert tracker.unused_parameters("repo#main", ".") == ["unused"]


def test_prompt_input_tracker_reports_ignored_templates():
    tracker = PromptInputTracker.from_json_string(
        """
        [
          {"template": "repo#main", "dest_folder": ".", "parameters": {}},
          {"template": "repo#main", "dest_folder": "src/api", "parameters": {}}
        ]
        """
    )

    tracker.get_template("repo#main", ".")

    ignored = tracker.ignored_templates()

    assert len(ignored) == 1
    assert ignored[0].template == "repo#main"
    assert ignored[0].dest_folder == "src/api"