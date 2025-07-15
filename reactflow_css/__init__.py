"""
This package provides styling utilities for ReactPy applications,
including integrations with Tailwind CSS and Bootstrap.
"""

__version__ = '1.0.6'

from .tailwindcss.Configuration import configure as configure_tailwind, default_css as default_tailwind

from .bootstrap.Configuration import configure as configure_boots, default_css as default_boots

from .bootstrap.generate import Convert_style as convert_imports_to_link

from . import tailwindcss
from . import bootstrap
from . import modules
from .modules import *

__all__ = [
    'tailwindcss',
    'bootstrap',
    'configure_boots',
    'configure_tailwind',
    'default_boots',
    'default_tailwind',
    'convert_imports_to_link'
]