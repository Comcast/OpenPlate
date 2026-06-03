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
from openplate.cfg.open_plate_settings import OpenPlateSettings
from openplate.sources.name_converter import convert_name


def prompt_template_reference(config_project_template):
    return config_project_template.raw_template_reference


def prompt_dest_folder(config_project_template):
    return config_project_template.raw_dest_folder


def prompt_condition(config_project_template):
    return config_project_template.raw_condition


def source_cache_key(settings: OpenPlateSettings, config_project_template):
    if config_project_template.src_url:
        return ("url", config_project_template.src_url)
    if config_project_template.src_name:
        return ("url", convert_name(settings, config_project_template.src_name))
    if config_project_template.src_folder:
        return ("folder", config_project_template.src_folder)
    raise ValueError("Unknown template source")