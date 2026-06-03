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
import json
from dataclasses import dataclass
from typing import Optional


def _require_optional_string(value, field_name: str):
    if value is not None and not isinstance(value, str):
        raise TypeError(f"Prompt parameter '{field_name}' must be a string or null")


def _require_optional_bool(value, field_name: str):
    if value is not None and not isinstance(value, bool):
        raise TypeError(f"Prompt parameter '{field_name}' must be a boolean or null")


@dataclass(frozen=True)
class PromptTemplateKey:
    template: str
    dest_folder: Optional[str]


@dataclass
class PromptParameterValue:
    value: Optional[str]
    default: Optional[str]
    existing: Optional[str]
    description: Optional[str]
    choices: Optional[list[str]]
    hidden: Optional[bool]
    required: Optional[bool]

    @classmethod
    def from_json_data(cls, data):
        if not isinstance(data, dict):
            raise TypeError("Prompt parameter entry must be an object")
        if "value" not in data:
            raise ValueError("Prompt parameter entry must include a 'value' field")

        choices = data.get("choices")
        if choices is not None and not isinstance(choices, list):
            raise TypeError("Prompt parameter 'choices' must be a list when provided")
        if choices is not None:
            for choice in choices:
                if not isinstance(choice, str):
                    raise TypeError("Prompt parameter 'choices' entries must be strings")

        _require_optional_string(data.get("value"), "value")
        _require_optional_string(data.get("default"), "default")
        _require_optional_string(data.get("existing"), "existing")
        _require_optional_string(data.get("description"), "description")
        _require_optional_bool(data.get("hidden"), "hidden")
        _require_optional_bool(data.get("required"), "required")

        return cls(
            data.get("value"),
            data.get("default"),
            data.get("existing"),
            data.get("description"),
            choices,
            data.get("hidden"),
            data.get("required"),
        )

    def to_json_data(self):
        return {
            "value": self.value,
            "default": self.default,
            "existing": self.existing,
            "description": self.description,
            "choices": self.choices,
            "hidden": self.hidden,
            "required": self.required,
        }


@dataclass
class PromptTemplateNode:
    template: str
    dest_folder: Optional[str]
    parameters: Optional[dict[str, PromptParameterValue]]
    condition: Optional[str] = None

    @property
    def key(self) -> PromptTemplateKey:
        return PromptTemplateKey(self.template, self.dest_folder)

    @classmethod
    def from_json_data(cls, data):
        if not isinstance(data, dict):
            raise TypeError("Prompt template entry must be an object")

        template = data.get("template")
        if not isinstance(template, str) or not template.strip():
            raise ValueError("Prompt template entry must include a non-empty 'template' field")

        if "dest_folder" not in data:
            raise ValueError("Prompt template entry must include a 'dest_folder' field")
        dest_folder = data.get("dest_folder")
        if dest_folder is not None and not isinstance(dest_folder, str):
            raise TypeError("Prompt template 'dest_folder' must be a string or null")

        if "parameters" not in data:
            raise ValueError("Prompt template entry must include a 'parameters' field")
        raw_parameters = data.get("parameters")
        parameters = None
        if raw_parameters is not None:
            if not isinstance(raw_parameters, dict):
                raise TypeError("Prompt template 'parameters' must be an object or null")
            parameters = {}
            for name, parameter_data in raw_parameters.items():
                if not isinstance(name, str) or not name:
                    raise ValueError("Prompt parameter names must be non-empty strings")
                parameters[name] = PromptParameterValue.from_json_data(parameter_data)

        condition = data.get("condition")
        if condition is not None and not isinstance(condition, str):
            raise TypeError("Prompt template 'condition' must be a string when provided")

        return cls(template.strip(), dest_folder, parameters, condition)

    def to_json_data(self):
        result = {
            "template": self.template,
            "dest_folder": self.dest_folder,
            "parameters": None,
        }
        if self.condition is not None:
            result["condition"] = self.condition
        if self.parameters is not None:
            result["parameters"] = {
                name: parameter.to_json_data()
                for name, parameter in self.parameters.items()
            }
        return result


@dataclass
class PromptDocument:
    templates: list[PromptTemplateNode]

    @classmethod
    def from_json_string(cls, json_string: str):
        raw_data = json.loads(json_string)
        if not isinstance(raw_data, list):
            raise TypeError("Prompt document must be a JSON array")

        templates = []
        seen_keys = set()
        for entry in raw_data:
            node = PromptTemplateNode.from_json_data(entry)
            if node.key in seen_keys:
                raise ValueError(
                    f"Duplicate prompt template entry: template={node.template!r}, dest_folder={node.dest_folder!r}"
                )
            seen_keys.add(node.key)
            templates.append(node)

        return cls(templates)

    def to_json_string(self) -> str:
        return json.dumps([node.to_json_data() for node in self.templates], indent=2)


class PromptDocumentBuilder:
    def __init__(self):
        self._templates = []
        self._seen_keys = set()

    def add_template(
        self,
        template: str,
        dest_folder: Optional[str],
        parameters: Optional[dict[str, PromptParameterValue]],
        condition: Optional[str] = None,
    ):
        key = PromptTemplateKey(template, dest_folder)
        if key in self._seen_keys:
            return False

        self._seen_keys.add(key)
        self._templates.append(PromptTemplateNode(template, dest_folder, parameters, condition))
        return True

    def build(self) -> PromptDocument:
        return PromptDocument(list(self._templates))


class PromptInputTracker:
    def __init__(self, document: Optional[PromptDocument]):
        self._document = document
        self._by_key = {}
        self._used_template_keys = set()
        self._used_parameter_names = {}

        if document is None:
            return

        for node in document.templates:
            self._by_key[node.key] = node
            self._used_parameter_names[node.key] = set()

    @classmethod
    def from_json_string(cls, json_string: str):
        return cls(PromptDocument.from_json_string(json_string))

    def get_template(self, template: str, dest_folder: Optional[str]) -> Optional[PromptTemplateNode]:
        key = PromptTemplateKey(template, dest_folder)
        node = self._by_key.get(key)
        if node is not None:
            self._used_template_keys.add(key)
        return node

    def mark_template_used(self, template: str, dest_folder: Optional[str]):
        key = PromptTemplateKey(template, dest_folder)
        if key in self._by_key:
            self._used_template_keys.add(key)

    def get_parameter_value(self, template: str, dest_folder: Optional[str], name: str):
        node = self.get_template(template, dest_folder)
        if node is None or node.parameters is None:
            return None, False

        parameter = node.parameters.get(name)
        if parameter is None:
            return None, False

        self._used_parameter_names[node.key].add(name)
        return parameter.value, True

    def ignored_templates(self) -> list[PromptTemplateNode]:
        if self._document is None:
            return []
        return [
            node for node in self._document.templates
            if node.key not in self._used_template_keys
        ]

    def unused_parameters(self, template: str, dest_folder: Optional[str]) -> list[str]:
        key = PromptTemplateKey(template, dest_folder)
        node = self._by_key.get(key)
        if node is None or node.parameters is None:
            return []

        used_names = self._used_parameter_names.get(key, set())
        unused = []
        for name, parameter in node.parameters.items():
            if parameter.value is None:
                continue
            if name not in used_names:
                unused.append(name)
        return unused