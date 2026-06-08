"""NL → hillm:// / gillm:// / tillm:// URI delegation."""

from __future__ import annotations

import re
import shlex
from typing import Literal
from urllib.parse import quote, urlencode

LlmDomain = Literal["hillm", "gillm", "tillm"]

_HARDWARE_RE = re.compile(
    r"\b("
    r"mysz(?:ka|ki)?|mouse|klawiatur(?:a|y|ę|e)?|keyboard|"
    r"kamer(?:a|y|ę|e)?|camera|webcam|usb|serial|rs232|rs485|"
    r"modbus|mqtt|sensor|czujnik|urządzen(?:ie|ia|)?|urzadzen(?:ie|ia|)?|"
    r"device|sprzęt|sprzet|hardware|port|portu|podłącz|podlacz|"
    r"temperatur(?:a|y|ę|e)?|hdmi|display|ekran|mikrofon|mic|"
    r"speaker|głośnik|glosnik|relay|przekaźnik|przekaznik|"
    r"ttyusb|ttyacm|lsusb|input|fieldbus"
    r")\b",
    re.IGNORECASE,
)
_QUESTION_RE = re.compile(
    r"(?:\?|^(?:czy|jak|jaki|jaka|jakie|jacy|na\s+jakim|który|ktora|ktore|"
    r"which|what|where|how|is|are|list)\b)",
    re.IGNORECASE,
)
_GILLM_RE = re.compile(
    r"\b(gillm|gui[- ]?llm|workflow|validate\s+file|simulate\s+file|"
    r"execute\s+file|focus\s+and\s+type|inject\s+text|orient\s+gui)\b",
    re.IGNORECASE,
)
_TILLM_CLIENTS = (
    "aider",
    "codex",
    "claude",
    "gemini",
    "devin",
    "opencode",
    "cursor-agent",
    "shell-gpt",
    "sgpt",
)
_TILLM_RE = re.compile(
    r"\b(tillm|shell[- ]?llm|drive\s+client|drive_matrix|"
    + "|".join(re.escape(c) for c in _TILLM_CLIENTS)
    + r")\b",
    re.IGNORECASE,
)


def _encode(value: str) -> str:
    return quote(str(value), safe="")


def hillm_uri_for_cmd(verb: str, **params: str | bool) -> str:
    query: dict[str, str] = {}
    for key in ("device", "register", "address", "value", "action", "category", "prompt"):
        raw = params.get(key)
        if raw:
            query[key] = str(raw)
    dry = params.get("dry_run")
    if dry is True or str(dry).lower() in {"1", "true", "yes", "on"}:
        query["dry_run"] = "true"
    suffix = f"?{urlencode(query, quote_via=quote)}" if query else ""
    return f"hillm://cmd/{verb.upper()}{suffix}"


def gillm_uri_for_cmd(verb: str, **params: str) -> str:
    query = {k: _encode(v) for k, v in params.items() if v}
    suffix = f"?{urlencode(query)}" if query else ""
    return f"gillm://cmd/{_encode(verb.upper())}{suffix}"


def tillm_uri_for_cmd(verb: str, **params: str) -> str:
    query = {k: _encode(v) for k, v in params.items() if v}
    suffix = f"?{urlencode(query)}" if query else ""
    return f"tillm://cmd/{_encode(verb.upper())}{suffix}"


def tillm_uri_for_client(client: str, *, prompt: str = "", project: str = "") -> str:
    uri = f"tillm://client/{_encode(client)}"
    parts: list[str] = []
    if prompt:
        parts.append(f"prompt={_encode(prompt)}")
    if project:
        parts.append(f"project={_encode(project)}")
    if parts:
        uri += "?" + "&".join(parts)
    return uri


def _payload_to_hillm_uri(payload: dict[str, object]) -> str:
    verb = str(payload.get("verb") or "HEALTH").upper()
    params: dict[str, str | bool] = {}
    for key in ("device", "register", "address", "value", "action", "category", "prompt"):
        if payload.get(key):
            params[key] = str(payload[key])
    if payload.get("dry_run"):
        params["dry_run"] = True
    return hillm_uri_for_cmd(verb, **params)


def dsl_to_hillm_uri(dsl_line: str) -> str:
    try:
        from dsl2hillm.grammar import parse_line
    except ImportError:
        return _simple_dsl_to_hillm_uri(dsl_line)
    payload = parse_line(dsl_line)
    if not payload:
        raise ValueError(f"invalid hillm DSL: {dsl_line!r}")
    return _payload_to_hillm_uri(payload)


def _simple_dsl_to_hillm_uri(dsl_line: str) -> str:
    tokens = dsl_line.strip().split()
    if not tokens:
        raise ValueError("empty hillm DSL")
    verb = tokens[0].upper()
    params: dict[str, str | bool] = {}
    idx = 1
    while idx < len(tokens):
        key = tokens[idx].lower()
        if key == "dry_run" and idx + 1 < len(tokens):
            params["dry_run"] = tokens[idx + 1].lower() in {"1", "true", "yes", "on"}
            idx += 2
            continue
        if idx + 1 < len(tokens):
            params[key] = tokens[idx + 1]
            idx += 2
            continue
        idx += 1
    return hillm_uri_for_cmd(verb, **params)


def dsl_to_gillm_uri(dsl_line: str) -> str:
    line = dsl_line.strip()
    upper = line.upper()
    if upper in {"HEALTH", "ORIENT", "ACTIONS", "CAPTURE"}:
        return gillm_uri_for_cmd(upper)
    if upper.startswith("PARSE "):
        prompt = line[5:].strip().strip('"')
        return gillm_uri_for_cmd("PARSE", instruction=prompt, prompt=prompt)
    if upper.startswith("VALIDATE FILE "):
        path = line.split(" ", 2)[2]
        return gillm_uri_for_cmd("VALIDATE", file=path)
    if upper.startswith("EXECUTE FILE "):
        path = line.split(" ", 2)[2]
        return gillm_uri_for_cmd("EXECUTE", file=path)
    raise ValueError(f"unsupported gillm DSL: {dsl_line!r}")


import shlex


def dsl_to_tillm_uri(dsl_line: str) -> str:
    line = dsl_line.strip()
    upper = line.upper()
    if upper in {"HEALTH", "CLIENTS", "ORIENT", "ACTIONS", "DOCKER_STATUS"}:
        return tillm_uri_for_cmd(upper)
    if upper.startswith("DRIVE CLIENT "):
        parts = shlex.split(line)
        client = parts[2] if len(parts) > 2 else "aider"
        prompt = ""
        execute = False
        idx = 3
        while idx < len(parts):
            if parts[idx].upper() == "PROMPT" and idx + 1 < len(parts):
                prompt = parts[idx + 1]
                idx += 2
                continue
            if parts[idx].upper() == "EXECUTE" and idx + 1 < len(parts):
                execute = parts[idx + 1].lower() in {"1", "true", "yes", "on"}
                idx += 2
                continue
            idx += 1
        if execute:
            return tillm_uri_for_cmd(
                "DRIVE",
                client=client,
                prompt=prompt,
                execute="true",
            )
        return tillm_uri_for_client(client, prompt=prompt)
    raise ValueError(f"unsupported tillm DSL: {dsl_line!r}")


def _hillm_to_dsl(prompt: str) -> str:
    try:
        from nlp2hillm.to_dsl import to_dsl

        return to_dsl(prompt)
    except ImportError:
        return _fallback_hillm_to_dsl(prompt)


def _fallback_hillm_to_dsl(prompt: str) -> str:
    text = prompt.strip()
    lower = text.lower()
    if not text:
        raise ValueError("empty prompt")
    if lower in {"health", "devices", "orient", "actions"}:
        return text.upper()
    if re.search(r"\b(mysz(?:ka|ki)?|mouse)\b", lower) and re.search(
        r"\b(port|portu|podłącz|podlacz|podłączon|podlaczon)\b", lower
    ):
        return "STATUS DEVICE mouse-default DRY_RUN true"
    if re.search(r"\b(klawiatur|keyboard)\b", lower) and re.search(
        r"\b(port|portu|podłącz|podlacz)\b", lower
    ):
        return "STATUS DEVICE keyboard-default DRY_RUN true"
    if re.search(r"\b(jakie\s+urządzenia|lista\s+urządzeń|list\s+devices|devices)\b", lower):
        return "DEVICES"
    if re.search(r"\b(health|stan\s+sprzętu|hardware\s+health)\b", lower):
        return "HEALTH"
    if re.search(r"\b(usb|lsusb)\b", lower) and _QUESTION_RE.search(text):
        return "DEVICES CATEGORY usb DRY_RUN true"
    device_match = _HARDWARE_RE.search(text)
    if device_match:
        device = device_match.group(1).lower()
        alias = {
            "mysz": "mouse",
            "myszka": "mouse",
            "myszki": "mouse",
            "klawiatura": "keyboard",
            "klawiaturę": "keyboard",
            "kamera": "camera",
            "mikrofon": "microphone",
            "mic": "microphone",
            "głośnik": "speaker",
            "glosnik": "speaker",
        }.get(device, device)
        if _QUESTION_RE.search(text) or re.search(r"\b(status|stan|info)\b", lower):
            return f"STATUS DEVICE {alias}-default DRY_RUN true"
        if re.search(r"\b(read|odczytaj|pobierz|temperatur)\b", lower):
            register = "temperature" if "temp" in lower else ""
            if register:
                return f"READ DEVICE sensor-temp REGISTER {register} DRY_RUN true"
            return f"READ DEVICE {alias}-default DRY_RUN true"
        return f"STATUS DEVICE {alias}-default DRY_RUN true"
    raise ValueError(f"could not map NL to hillm DSL: {prompt!r}")


def _gillm_to_dsl(prompt: str) -> str:
    try:
        from nlp2gillm.to_dsl import to_dsl

        return to_dsl(prompt)
    except ImportError:
        return _fallback_gillm_to_dsl(prompt)


def _fallback_gillm_to_dsl(prompt: str) -> str:
    text = prompt.strip()
    lower = text.lower()
    if "health" in lower or "status" in lower:
        return "HEALTH"
    if "orient" in lower:
        return "ORIENT"
    if "workflow" in lower and "execute" in lower:
        return "EXECUTE FILE workflow.json"
    if "validate" in lower:
        return "VALIDATE FILE workflow.json"
    if re.search(r"focus.+type", lower):
        return f'PARSE "{text}"'
    if "capture" in lower or "screenshot" in lower:
        return "CAPTURE"
    raise ValueError(f"could not map NL to gillm DSL: {prompt!r}")


def _tillm_to_dsl(prompt: str) -> str:
    try:
        from nlp2tillm.to_dsl import to_dsl

        return to_dsl(prompt)
    except ImportError:
        return _fallback_tillm_to_dsl(prompt)


def _fallback_tillm_to_dsl(prompt: str) -> str:
    text = prompt.strip()
    lower = text.lower()
    if lower in {"health", "clients", "orient", "actions"}:
        return text.upper()
    for client in _TILLM_CLIENTS:
        if client in lower:
            body = text
            for sep in (":", "->", "=>"):
                if sep in text:
                    head, tail = text.split(sep, 1)
                    if client in head.lower():
                        body = tail.strip()
                        break
            escaped = body.replace('"', '\\"')
            return f'DRIVE CLIENT {client} PROMPT "{escaped}"'
    if re.search(r"\b(run|drive|uruchom)\b", lower):
        escaped = text.replace('"', '\\"')
        return f'DRIVE CLIENT aider PROMPT "{escaped}"'
    raise ValueError(f"could not map NL to tillm DSL: {prompt!r}")


def prompt_to_hillm_uri(prompt: str) -> str | None:
    text = prompt.strip()
    if not text or not _HARDWARE_RE.search(text):
        return None
    try:
        return dsl_to_hillm_uri(_hillm_to_dsl(text))
    except ValueError:
        return None


def prompt_to_gillm_uri(prompt: str) -> str | None:
    text = prompt.strip()
    if not text or not _GILLM_RE.search(text):
        return None
    try:
        return dsl_to_gillm_uri(_gillm_to_dsl(text))
    except ValueError:
        return None


def prompt_to_tillm_uri(prompt: str) -> str | None:
    text = prompt.strip()
    if not text or not _TILLM_RE.search(text):
        return None
    try:
        return dsl_to_tillm_uri(_tillm_to_dsl(text))
    except ValueError:
        return None


def resolve_llm_prompt(prompt: str) -> tuple[LlmDomain, str] | None:
    """Return (domain, uri) when prompt matches hillm/gillm/tillm heuristics."""
    for domain, resolver in (
        ("hillm", prompt_to_hillm_uri),
        ("gillm", prompt_to_gillm_uri),
        ("tillm", prompt_to_tillm_uri),
    ):
        uri = resolver(prompt)
        if uri:
            return domain, uri  # type: ignore[return-value]
    return None
