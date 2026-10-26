# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import TypeGuard

EXTRACTED_FILES = "py/diagnostics/successfully-extracted-files"
HARMLESS_LEVELS = ("none", "note")
JSON_WHITESPACE = " \t\n\r"


def _is_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def _is_mapping(value: object) -> TypeGuard[Mapping[object, object]]:
    return isinstance(value, dict)


def _is_object(value: object) -> TypeGuard[Mapping[str, object]]:
    return _is_mapping(value) and all(isinstance(key, str) for key in value)


def _field(value: object, key: str, default: object = None) -> object:
    return value.get(key, default) if _is_object(value) else default


def _parse(text: str) -> object:
    document = text.strip(JSON_WHITESPACE)
    decoded: tuple[object, int] = json.JSONDecoder().raw_decode(document)
    value, end = decoded
    if end != len(document):
        message = "CodeQL report holds more than 1 JSON value."
        raise ValueError(message)
    return value


def _items(value: object, name: str) -> list[Mapping[str, object]]:
    if _is_list(value):
        items = [item for item in value if _is_object(item)]
        if items and len(items) == len(value):
            return items
    message = f"CodeQL report lacks {name}."
    raise ValueError(message)


def _describe(finding: object) -> str:
    locations = _field(finding, "locations")
    first = locations[0] if _is_list(locations) and locations else None
    location = _field(first, "physicalLocation")
    file = _field(_field(location, "artifactLocation"), "uri", "unknown file")
    line = _field(_field(location, "region"), "startLine", 0)
    text = _field(_field(finding, "message"), "text", "")
    return f"{_field(finding, 'ruleId')} {file}:{line} {text}".strip()


def validate(report: object) -> str:
    runs = _items(_field(report, "runs"), "runs")
    if _field(report, "version") != "2.1.0" or len(runs) != 1:
        message = "Expected 1 SARIF 2.1.0 run."
        raise ValueError(message)
    findings = runs[0].get("results")
    if not _is_list(findings):
        message = "CodeQL report lacks results."
        raise ValueError(message)
    if findings:
        places = "\n".join(_describe(finding) for finding in findings)
        message = f"{places}\nCodeQL found {len(findings)} finding(s). Fix each one."
        raise ValueError(message)
    extracted = 0
    for invocation in _items(runs[0].get("invocations"), "invocations"):
        if invocation.get("executionSuccessful") is not True:
            message = "CodeQL invocation failed."
            raise ValueError(message)
        for notification in _items(
            invocation.get("toolExecutionNotifications"), "diagnostics"
        ):
            if notification.get("level") not in HARMLESS_LEVELS:
                message = "CodeQL diagnostic needs review."
                raise ValueError(message)
            descriptor = _field(notification.get("descriptor"), "id")
            extracted += descriptor == EXTRACTED_FILES
    if not extracted:
        message = "CodeQL did not confirm extracted Python files."
        raise ValueError(message)
    return f"CodeQL finished with no findings. Extracted Python entries {extracted}."


if __name__ == "__main__":
    try:
        sys.stdout.write(validate(_parse(Path(sys.argv[1]).read_text())) + "\n")
    except ValueError as error:
        sys.exit(str(error))
