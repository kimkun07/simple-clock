import re
from datetime import datetime

_VARS = re.compile(r"\{(HH|mm|ss|YYYY|MM|DD|ddd)\}")

# (template_start, template_token_len, rendered_start, rendered_token_len)
OffsetMap = list[tuple[int, int, int, int]]


def render(template_text: str, now: datetime) -> tuple[str, OffsetMap]:
    """Return (rendered_text, offset_map) for variable substitution."""

    def _sub(var: str) -> str:
        match var:
            case "HH":
                return now.strftime("%H")
            case "mm":
                return now.strftime("%M")
            case "ss":
                return now.strftime("%S")
            case "YYYY":
                return now.strftime("%Y")
            case "MM":
                return now.strftime("%m")
            case "DD":
                return now.strftime("%d")
            case "ddd":
                return now.strftime("%a")
        return var

    offset_map: OffsetMap = []
    parts: list[str] = []
    t_pos = 0
    r_pos = 0

    for m in _VARS.finditer(template_text):
        literal = template_text[t_pos : m.start()]
        parts.append(literal)
        r_pos += len(literal)

        replacement = _sub(m.group(1))
        t_tok_len = m.end() - m.start()
        r_tok_len = len(replacement)
        offset_map.append((m.start(), t_tok_len, r_pos, r_tok_len))
        parts.append(replacement)

        t_pos = m.end()
        r_pos += r_tok_len

    parts.append(template_text[t_pos:])
    return "".join(parts), offset_map


def remap_position(template_pos: int, offset_map: OffsetMap) -> int:
    """Map a template-space character position to rendered-space."""
    adjustment = 0
    for t_start, t_len, _r_start, r_len in offset_map:
        if template_pos <= t_start:
            break
        if template_pos < t_start + t_len:
            # Position is inside a token — snap to end of rendered token
            return _r_start + r_len
        adjustment += r_len - t_len
    return template_pos + adjustment


def remap_run(start: int, length: int, offset_map: OffsetMap) -> tuple[int, int]:
    """Map a template-space (start, length) run to rendered-space."""
    r_start = remap_position(start, offset_map)
    r_end = remap_position(start + length, offset_map)
    return r_start, max(0, r_end - r_start)
