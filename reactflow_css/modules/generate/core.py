import json
import os
import sys
import re
from pathlib import Path
from reactpy import component, html, hooks, run
from typing import Dict, Any, List, Union, Optional


class CSSLinkConverter:
    """Utility class for converting CSS @import statements to HTML link elements."""
    
    # Regex patterns for different @import formats
    IMPORT_PATTERNS = [
        r'@import\s+(?:url\s*\(\s*)?["\']([^"\']+)["\'](?:\s*\))?(?:\s*[^;]*)?;?',
        r'@import\s+url\s*\(\s*([^)]+)\s*\)(?:\s*[^;]*)?;?',
        r'@import\s+([^;]+);?'
    ]
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the converter with a base path.
        
        Args:
            base_path: Base path for resolving relative imports. 
                      Defaults to parent/bootstrap directory.
        """
        if base_path is None:
            self.base_path = Path(__file__).parent / '..' / 'bootstrap'
        else:
            self.base_path = Path(base_path)
    
    def extract_imports(self, css_content: str) -> List[str]:
        """
        Extract all @import paths from CSS content.
        
        Args:
            css_content: CSS string containing @import statements.
            
        Returns:
            List of import paths found in the CSS.
        """
        imports = []
        
        for pattern in self.IMPORT_PATTERNS:
            matches = re.findall(pattern, css_content, re.IGNORECASE | re.MULTILINE)
            imports.extend(matches)
        
        return [self._clean_path(path) for path in imports]
    
    def _clean_path(self, path: str) -> str:
        """Clean and normalize import path."""
        # Remove quotes and whitespace
        path = path.strip().strip('"\'')
        
        # Remove url() wrapper if present
        if path.startswith('url(') and path.endswith(')'):
            path = path[4:-1].strip().strip('"\'')
        
        return path
    
    def resolve_path(self, import_path: str) -> str:
        """
        Resolve import path to actual href.
        
        Args:
            import_path: The import path to resolve.
            
        Returns:
            Resolved href for the link element.
        """
        clean_path = self._clean_path(import_path)
        
        # Handle different path types
        if clean_path.startswith(('http://', 'https://', 'ftp://', 'ftps://')):
            # Absolute URL (web protocols)
            return clean_path
        elif clean_path.startswith('/'):
            # Absolute path from root
            return clean_path
        elif clean_path.startswith('--/'):
            # Custom notation for bootstrap path
            return clean_path.replace('--/', f'{str(self.base_path)}/')
        elif clean_path.startswith(('../', './')):
            # Relative paths (including parent directory navigation)
            # Keep as-is for proper relative path resolution
            return clean_path
        elif clean_path.startswith('..'):
            # Parent directory without slash (e.g., "..\\file.css")
            # Normalize to forward slash
            return clean_path.replace('\\', '/')
        else:
            # Regular filename without path indicators
            # Keep as-is to preserve original behavior
            return clean_path
    
    def create_link_element(self, href: str) -> Dict[str, Any]:
        """
        Create HTML link element dictionary.
        
        Args:
            href: The href attribute value.
            
        Returns:
            Dictionary representing HTML link element.
        """
        return html.link({
            "href": href,
            "rel": "stylesheet",
            "type": "text/css"
        })
    
    def convert_to_links(self, css_content: str) -> List[Dict[str, Any]]:
        """
        Convert CSS @import statements to HTML link elements.
        
        Args:
            css_content: CSS string containing @import statements.
            
        Returns:
            List of HTML link elements.
        """
        imports = self.extract_imports(css_content)
        link_elements = []
        
        for import_path in imports:
            href = self.resolve_path(import_path)
            link_element = self.create_link_element(href)
            link_elements.append(link_element)
        
        return link_elements


@component
def convert_links(
    style: Optional[str] = None, 
    links: Optional[List[str]] = None,
    base_path: Optional[str] = None
) -> html.div:
    """
    ReactPy component to convert CSS with @import rules into HTML link elements.
    
    Args:
        style: String containing CSS with @import statements.
        links: List of import paths (alternative to parsing from style).
        base_path: Base path for resolving relative imports.
        
    Returns:
        HTML div element containing link elements for each @import found.
    """
    # Initialize converter
    converter = CSSLinkConverter(base_path)
    
    # Determine input source
    if style:
        # Extract imports from CSS content
        link_elements = converter.convert_to_links(style)
    elif links:
        # Use provided links directly
        link_elements = []
        for link in links:
            href = converter.resolve_path(link)
            link_element = converter.create_link_element(href)
            link_elements.append(link_element)
    else:
        # No input provided
        link_elements = []
    
    # Return wrapped in div element
    return html.div(link_elements)


@component
def css_import_parser(css_file_path: Optional[str] = None) -> html.div:
    """
    Enhanced component that can also read CSS from file.
    
    Args:
        css_file_path: Path to CSS file to parse.
        
    Returns:
        HTML div element containing parsed link elements.
    """
    link_elements = []
    
    if css_file_path:
        try:
            css_path = Path(css_file_path)
            if css_path.exists():
                css_content = css_path.read_text(encoding='utf-8')
                converter = CSSLinkConverter()
                link_elements = converter.convert_to_links(css_content)
            else:
                # Return error message if file doesn't exist
                return html.div(
                    html.p(f"Error: CSS file not found: {css_file_path}"),
                    {"style": {"color": "red"}}
                )
        except Exception as e:
            # Return error message for any other exceptions
            return html.div(
                html.p(f"Error reading CSS file: {str(e)}"),
                {"style": {"color": "red"}}
            )
    
    return html.div(link_elements)


# Example usage and testing
if __name__ == "__main__":
    # Test CSS content with various path types
    test_css = """
    @import "bootstrap.css";
    @import url("theme.css");
    @import url(https://fonts.googleapis.com/css2?family=Roboto);
    @import "--/custom.css";
    @import "../files/icons/icons.css";
    @import "./styles/main.css";
    @import "../../shared/common.css";
    @import url("../assets/fonts.css");
    
    body {
        font-family: Arial, sans-serif;
    }
    """
    
    # Test the converter
    converter = CSSLinkConverter()
    imports = converter.extract_imports(test_css)
    print("Found imports:", imports)
    
    # Test path resolution
    test_paths = [
        "bootstrap.css",
        "../files/icons/icons.svg",
        "./styles/main.css",
        "../../shared/common.css",
        "https://example.com/style.css",
        "/absolute/path.css",
        "--/custom.css"
    ]
    
    print("\nPath resolution test:")
    for path in test_paths:
        resolved = converter.resolve_path(path)
        print(f"  {path} → {resolved}")
    
    # Test component (would need ReactPy environment to run)
    # component_result = convert_links(style=test_css)
    # print("Component result:", component_result)