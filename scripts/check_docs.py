"""Verifica destinos locales de enlaces Markdown, incluidos nombres con espacios."""

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
errors = []
paths = [*ROOT.glob("*.md"), *ROOT.glob("docs/**/*.md"), *ROOT.glob(".github/**/*.md")]
for path in paths:
    # Los ejemplos de código pueden contener Markdown literal.
    content = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", content):
        target = target.strip().strip("<>")
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = unquote(target.split("#", 1)[0])
        if target and not (path.parent / target).exists():
            errors.append(f"{path.relative_to(ROOT)}: {target}")
if errors:
    raise SystemExit("Enlaces inexistentes:\n" + "\n".join(errors))
print(f"Enlaces locales válidos en {len(paths)} documentos")
