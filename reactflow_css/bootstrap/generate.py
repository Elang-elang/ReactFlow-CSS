import json
import os
import sys
import re
from pathlib import Path
from reactpy import component, html, hooks, run
from typing import Dict, Any, List, Union, Optional

files_dirs = Path(__file__).parent
files_dirs = files_dirs / '..' / 'modules' / 'bootstrap'

@component
def Convert_style(style: str):
    """
    Component to convert CSS with @import rules into HTML link elements.
    
    Args:
        style: String containing CSS with @import statements.
        
    Returns:
        List of HTML link elements for each @import found.
    """
    
    # Regex pattern to capture @import statements
    # Supports various formats: @import "path", @import 'path', @import url("path"), etc.
    import_pattern = r"""@import\s+(?:url\s*\(\s*)?["\\]([^\]']+)["\\](?:\s*\))?(?:\s*[^;]*)?;?"""
    
    # Find all @import statements in CSS
    imports = re.findall(import_pattern, style, re.IGNORECASE)
    
    # List to store link elements
    link_elements = []
    
    # Loop through each found import
    for import_path in imports:
        # Clean the path from unnecessary characters
        clean_path = import_path.strip()
        
        # Handle relative and absolute paths
        if clean_path.startswith(('http://', 'https://')):
            # Absolute URL
            href = clean_path
        elif clean_path.startswith('/'):
            # Absolute path from root
            href = clean_path
        elif clean_path.startswith('--/'):
            href = clean_path.replace('--/', f'{str(files_dirs)}/' )
        else:
            # Relative path - adjust according to your project structure
            # For example, if CSS is in the css/ folder, the relative path will be adjusted
            href = f"./css/{clean_path}" if not clean_path.startswith('./') else clean_path
        
        # Create HTML link element
        link_element = html.link({
            "href": href,
            "rel": "stylesheet",
            "type": "text/css"
        })
        
        link_elements.append(link_element)
    
    # Return list of link elements
    return html.div([i for i in link_elements])