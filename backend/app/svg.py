import html
import re


def make_svg(text: str, color: str = "#315a81") -> str:
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError("Color must be a six-digit hex value")
    escaped = html.escape(text, quote=True)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" '
        'viewBox="0 0 800 400">'
        f'<rect width="800" height="400" fill="{color}"/>'
        '<foreignObject x="40" y="40" width="720" height="320">'
        '<div xmlns="http://www.w3.org/1999/xhtml" '
        'style="color:white;font:24px sans-serif;overflow-wrap:anywhere">'
        f'{escaped}</div></foreignObject></svg>'
    )
