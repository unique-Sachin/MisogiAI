from pathlib import Path
from typing import Any
import os

from jinja2 import Environment, FileSystemLoader, TemplateNotFound  # type: ignore

from .config import settings

TEMPLATES_DIR = Path(os.getenv("TEMPLATES_DIR", "templates"))
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,  # plain text emails
    trim_blocks=True,
    lstrip_blocks=True,
)

_DEFAULT_TEMPLATE_NAME = "email_default.jinja"

# Ensure a default template exists so first run works without manual setup
_default_template_path = TEMPLATES_DIR / _DEFAULT_TEMPLATE_NAME
if not _default_template_path.exists():
    _default_template_path.write_text(
        """Hello{{ ' ' + recipient_name if recipient_name else ',' }}\n\n{{ body }}\n\nBest regards,\n{{ signature }}\n\n{{ disclaimer }}\n""",
        encoding="utf-8",
    )


class TemplateRenderer:
    """Render email responses using Jinja2 templates."""

    def __init__(self, template_name: str = _DEFAULT_TEMPLATE_NAME):
        try:
            self.template = _env.get_template(template_name)
        except TemplateNotFound:
            # Fallback to default if specific template missing
            self.template = _env.get_template(_DEFAULT_TEMPLATE_NAME)

    def render(self, body: str, recipient_name: str = "", **kwargs: Any) -> str:
        context = {
            "body": body.strip(),
            "recipient_name": recipient_name.strip(),
            "signature": settings.SIGNATURE,
            "disclaimer": settings.DISCLAIMER,
            **kwargs,
        }
        return self.template.render(**context).strip() + "\n" 