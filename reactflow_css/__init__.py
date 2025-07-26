"""
This package provides styling utilities for ReactPy applications,
including integrations with Tailwind CSS and Bootstrap.
"""

__version__ = '2.1.0'

from .tailwindcss.Configuration import configure as configure_tailwind, default_css as default_tailwind

from .bootstrap.Configuration import configure as configure_boots, default_css as default_boots

from .modules.generate.core import CSSLinkConverter

from .icons.generate import create_icon_generator, get_icon

extract_imports = lambda content: CSSLinkConverter.extract_imports(css_content = content)
resolve_path = lambda content: CSSLinkConverter.resolve_path(import_path = content)

__all__ = [
    'tailwindcss',
    'bootstrap',
    'configure_boots',
    'configure_tailwind',
    'default_boots',
    'default_tailwind',
    'extract_imports',
    'resolve_path',
    'create_icon_generator',
    'get_icon'
]

from .cli import cli