from __future__ import annotations

import base64
import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_MEDIA_RE = re.compile(r"^\[MEDIA_PAYLOAD:(?P<path>[^\]]+)\]\s*(?P<instruction>.*)$", re.DOTALL)


@dataclass(frozen=True)
class MediaPayload:
    path: Path
    instruction: str
    media_type: str
    data_b64: str


def parse_media_payload(prompt: str) -> Optional[MediaPayload]:
    match = _MEDIA_RE.match(prompt.strip())
    if not match:
        return None

    path = Path(match.group("path")).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Media payload does not exist: {path}")

    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return MediaPayload(
        path=path,
        instruction=match.group("instruction").strip() or "Analyze the attached image.",
        media_type=media_type,
        data_b64=base64.b64encode(path.read_bytes()).decode("ascii"),
    )
