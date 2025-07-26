import os
import json
import base64
from pathlib import Path
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum

from .exceptions import GenerateIconErrors, ModuleNotFound, ProcessError


class IconStyle(Enum):
    """Available icon styles"""
    FILLED = "filled"
    OUTLINED = "outlined"
    ROUND = "round"
    SHARP = "sharp"
    TWO_TONE = "two-tone"


@dataclass
class IconConfig:
    """Configuration for the icon generator"""
    output_dir: str = "output"
    css_filename: str = "icons.css"
    css_prefix: str = "icon"
    icon_styles: List[IconStyle] = None
    include_size_variants: bool = True
    size_variants: List[str] = None
    naming_pattern: str = "prefix_style_icon"  # atau "folder_icon"
    
    def __post_init__(self):
        if self.icon_styles is None:
            self.icon_styles = list(IconStyle)
        if self.size_variants is None:
            self.size_variants = ["16", "24", "32", "48"]


class ReactPyIconGenerator:
    """SVG icon generator for ReactPy with CSS background-image using base64"""
    
    def __init__(self, config: Optional[IconConfig] = None):
        self.config = config or IconConfig()
        
        # Absolute path to the package icons directory
        self.package_path_input = Path(__file__).parent.absolute()
        self.icons_path_input = self.package_path_input / "icons"
        
        # Output directory (user-configurable)
        self.path_output = Path(self.config.output_dir)
        self.path_output.mkdir(parents=True, exist_ok=True)
        
        # Validate icons directory exists
        if not self.icons_path_input.exists():
            raise ModuleNotFound(f"Icons directory not found: {self.icons_path_input}")
        
        # Debug: Print struktur direktori yang ditemukan
        self._debug_directory_structure()
    
    def _debug_directory_structure(self):
        """Debug method untuk melihat struktur direktori"""
        try:
            for item in self.icons_path_input.iterdir():
                if item.is_dir():
                    svg_files = list(item.glob("*.svg"))
        except Exception as e:
            raise ProcessError(f"Error reading directory structure: {e}")
    
    def _get_icon_path(self, icon_name: str, style: IconStyle) -> Optional[Path]:
        """Get absolute path to icon file dengan error handling yang lebih baik"""
        filename = f"{icon_name}.svg"
        icon_path_input = self.icons_path_input / style.value / filename
        
        if not icon_path_input.exists():
            # Coba alternatif path jika struktur berbeda
            alternative_path_input = self.icons_path_input / filename
            if alternative_path_input.exists():
                return alternative_path_input
        
        return icon_path_input if icon_path_input.exists() else None
    
    def _svg_to_base64(self, svg_path_input: Path) -> Optional[str]:
        """
        Convert SVG file to base64 string dengan error handling yang lebih baik
        
        Args:
            svg_path_input: Path to the SVG file
            
        Returns:
            Base64 string or None if it fails
        """
        try:
            # Validasi file ada dan readable
            if not svg_path_input.exists():
                raise ModuleNotFound(f"SVG file not found: '{svg_path_input}'")
            
            if not svg_path_input.is_file():
                raise ModuleNotFound(f"Path is not a file: {svg_path_input}")
            
            # Read SVG file as binary
            with svg_path_input.open('rb') as f:
                svg_data = f.read()
            
            # Validasi data tidak kosong
            if not svg_data:
                raise ModuleNotFound(f"SVG file is empty: {svg_path_input}")
            
            # Convert to base64
            base64_data = base64.b64encode(svg_data).decode('utf-8')
            
            # Return as a data URI for SVG
            return f"data:image/svg+xml;base64,{base64_data}"
            
        except Exception as e:
            raise ProcessError(f"Error converting SVG to base64 ({svg_path_input}): {e}")
    
    def _scan_available_icons(self) -> Dict[str, List[str]]:
        """Scan all available icons dengan logika yang diperbaiki"""
        catalog = {}
        
        try:
            for style in self.config.icon_styles:
                style_path_input = self.icons_path_input / style.value
                icons = []
                
                if not style_path_input.exists():
                    # Jika style directory tidak ada, coba scan di root icons directory
                    # untuk style pertama saja
                    if style == self.config.icon_styles[0]:
                        for svg_file in self.icons_path_input.glob("*.svg"):
                            icon_name = svg_file.stem
                            icons.append(icon_name)
                    catalog[style.value] = sorted(set(icons))
                    continue
                
                # Scan SVG files dalam direktori style
                svg_files = list(style_path_input.glob("*.svg"))
                
                for svg_file in svg_files:
                    icon_name = svg_file.stem
                    icons.append(icon_name)
                
                catalog[style.value] = sorted(set(icons))
                
        except Exception as e:
            raise ProcessError(f"Error scanning available icons: {e}")
        
        return catalog
    
    def _generate_css_rule(self, icon_name: str, style: IconStyle, size: Optional[str] = None) -> Optional[str]:
        """Generate CSS rule dengan penamaan yang fleksibel"""
        icon_path_input = self._get_icon_path(icon_name, style)
        if not icon_path_input:
            raise ModuleNotFound(f"Icon not found: {icon_name} in style {style.value}")
        
        # Convert SVG to base64
        base64_data = self._svg_to_base64(icon_path_input)
        if not base64_data:
            raise ProcessError(f"Failed to convert to base64: {icon_path_input}")
        
        # Generate CSS class name berdasarkan pattern yang diinginkan
        if self.config.naming_pattern == "folder_icon":
            # Pattern: .[namafolder]_[namaIcon]
            class_name = f".{style.value}_{icon_name.replace('-', '_')}"
        else:
            # Pattern default: .prefix-style-icon
            class_name = f".{self.config.css_prefix}-{style.value}-{icon_name.replace('_', '-')}"
        
        if size:
            class_name += f"-{size}"
        
        # Generate CSS dengan base64 data URI
        css_rule = f"{class_name} {{\n"
        css_rule += f"    background-image: url('{base64_data}');\n"
        css_rule += f"    background-repeat: no-repeat;\n"
        css_rule += f"    background-position: center;\n"
        css_rule += f"    background-size: contain;\n"
        css_rule += f"    display: inline-block;\n"
        css_rule += f"    width: {size}px;\n" if size else f"    width: 24px;\n"
        css_rule += f"    height: {size}px;\n" if size else f"    height: 24px;\n"
        css_rule += f"}}"
        return css_rule
    
    def get_icon_base64(self, icon_name: str, style: Union[str, IconStyle] = IconStyle.FILLED) -> Optional[str]:
        """
        Get base64 data URI for a ReactPy component
        
        Args:
            icon_name: Icon name
            style: Icon style
            
        Returns:
            Base64 data URI string or None
        """
        try:
            if isinstance(style, str):
                style = IconStyle(style)
            
            icon_path_input = self._get_icon_path(icon_name, style)
            if icon_path_input:
                return self._svg_to_base64(icon_path_input)
            
            return None
            
        except ValueError:
            raise ProcessError(f"Invalid style: {style}")
        except Exception as e:
            raise ProcessError(f"Error getting icon base64: {e}")
    
    def get_icon_path(self, icon_name: str, style: Union[str, IconStyle] = IconStyle.FILLED) -> Optional[str]:
        """
        Get file path for a ReactPy component (for backward compatibility)
        
        Args:
            icon_name: Icon name
            style: Icon style
            
        Returns:
            File path string or None
        """
        try:
            if isinstance(style, str):
                style = IconStyle(style)
            
            icon_path_input = self._get_icon_path(icon_name, style)
            if icon_path_input:
                return str(icon_path_input)
            
            return None
            
        except ValueError:
            return None
        except Exception as e:
            raise ProcessError(f"Error getting icon path: {e}")
    
    def generate_css_file(self, icon_filter: Optional[List[str]] = None) -> str:
        """
        Generate a CSS file for all icons using base64 dengan validasi yang lebih baik
        
        Args:
            icon_filter: Filter for icons to be generated
            
        Returns:
            CSS content string
        """
        catalog = self._scan_available_icons()
        
        if not catalog:
            return "/* No icons found */"
        
        css_rules = []
        
        # CSS Header
        css_rules.append("/* ReactPy Icon Generator - Auto Generated (Base64) */")
        css_rules.append("/* Generated icons from directory structure */")
        css_rules.append("/* Base icon styles */")
        css_rules.append(f"[class^=\"{self.config.css_prefix}-\"], [class*=\"_\"] {{")
        css_rules.append("    display: inline-block;")
        css_rules.append("    background-repeat: no-repeat;")
        css_rules.append("    background-position: center;")
        css_rules.append("    background-size: contain;")
        css_rules.append("}")
        css_rules.append("")
        
        # Generate rules for each icon
        total_rules = 0
        for style in self.config.icon_styles:
            if style.value not in catalog:
                continue
            
            available_icons = catalog[style.value]
            target_icons = icon_filter if icon_filter else available_icons
            
            for icon_name in target_icons:
                if icon_name not in available_icons:
                    continue
                
                try:
                    # Default size
                    rule = self._generate_css_rule(icon_name, style)
                    if rule:
                        css_rules.append(rule)
                        total_rules += 1
                    
                    # Size variants
                    if self.config.include_size_variants:
                        for size in self.config.size_variants:
                            rule = self._generate_css_rule(icon_name, style, size)
                            if rule:
                                css_rules.append(rule)
                                total_rules += 1
                                
                except Exception as e:
                    continue
        
        if total_rules == 0:
            css_rules.append("/* No valid icons found to generate rules */")
        
        return '\n\n'.join(css_rules)
    
    def save_css_file(self, icon_filter: Optional[List[str]] = None) -> bool:
        """Save the CSS file to disk dengan validasi yang lebih baik"""
        try:
            css_content = self.generate_css_file(icon_filter)
            
            if not css_content or css_content.strip() == "/* No icons found */":
                raise ProcessError("No CSS content generated!")
            
            css_path_output = self.path_output / self.config.css_filename
            
            with css_path_output.open('w', encoding='utf-8') as f:
                f.write(css_content)
            
            return True
            
        except Exception as e:
            raise ProcessError(f"Error saving CSS file: {e}")
    
    def get_available_icons(self) -> Dict[str, List[str]]:
        """Get a list of all available icons"""
        return self._scan_available_icons()
    
    def generate_icon_catalog_base64(self, icon_filter: Optional[List[str]] = None) -> Dict[str, Dict[str, str]]:
        """
        Generate a catalog of all icons with base64 data
        
        Args:
            icon_filter: Filter for icons to be generated
            
        Returns:
            Dictionary with the structure: {style: {icon_name: base64_data}}
        """
        catalog = {}
        available_icons = self._scan_available_icons()
        
        for style in self.config.icon_styles:
            if style.value not in available_icons:
                continue
            
            catalog[style.value] = {}
            target_icons = icon_filter if icon_filter else available_icons[style.value]
            
            for icon_name in target_icons:
                if icon_name not in available_icons[style.value]:
                    continue
                
                try:
                    base64_data = self.get_icon_base64(icon_name, style)
                    if base64_data:
                        catalog[style.value][icon_name] = base64_data
                except Exception as e:
                    continue
        
        return catalog
    
    def save_icon_catalog_json(self, icon_filter: Optional[List[str]] = None) -> bool:
        """
        Save the icon catalog in JSON format with base64 data
        
        Args:
            icon_filter: Filter for icons to be saved
            
        Returns:
            True if successful, False if it fails
        """
        try:
            catalog = self.generate_icon_catalog_base64(icon_filter)
            json_path_output = self.path_output / "icon_catalog.json"
            
            with json_path_output.open('w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            raise ProcessError(f"Error saving icon catalog: {e}")
    
    def build(self, icon_filter: Optional[List[str]] = None) -> Dict:
        """
        Build the CSS and JSON catalog dengan logging yang lebih baik
        
        Args:
            icon_filter: Filter for icons to be built
            
        Returns:
            Build result dictionary
        """
        
        result = {
            'success': False,
            'css_file': None,
            'json_file': None,
            'available_icons': {},
            'total_icons': 0,
            'errors': []
        }
        
        try:
            # Generate CSS
            css_success = self.save_css_file(icon_filter)
            if css_success:
                result['css_file'] = str(self.path_output / self.config.css_filename)
            else:
                result['errors'].append("Failed to generate CSS file")
                
            # Generate JSON catalog
            json_success = self.save_icon_catalog_json(icon_filter)
            if json_success:
                result['json_file'] = str(self.path_output / "icon_catalog.json")
            else:
                result['errors'].append("Failed to generate JSON catalog")
            
            # Get available icons
            available_icons = self.get_available_icons()
            result['available_icons'] = available_icons
            result['total_icons'] = sum(len(icons) for icons in available_icons.values())
            result['success'] = css_success and json_success
                
        except Exception as e:
            error_msg = f"Build error: {e}"
            result['errors'].append(error_msg)
            result['success'] = False
            raise ProcessError(error_msg)
        
        return result


def create_icon_generator(output_path: str, save_logs: bool = False, icon_filter: Optional[List[str]] = None, icons: Optional[List[str]] = None) -> bool:
    """
    Generate CSS file with icons to specified output path
    
    Args:
        output_path: Full path for the output CSS file (e.g., "/path/to/output.css")
        save_logs: Whether to save logs (currently not implemented)
        icon_filter: List of icon styles to filter ("filled", "outlined", "round", "sharp", "two-tone")
        icons: List of specific icon names to generate (if None, generates all icons)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Parse output path
        output_file = Path(output_path)
        output_dir = output_file.parent
        css_filename = output_file.name
        
        # Determine which styles to include
        available_styles = [IconStyle.FILLED, IconStyle.OUTLINED, IconStyle.ROUND, IconStyle.SHARP, IconStyle.TWO_TONE]
        
        if icon_filter:
            # Filter styles based on icon_filter parameter
            filtered_styles = []
            for style_name in icon_filter:
                try:
                    style = IconStyle(style_name.lower().replace("-", "_"))
                    if style in available_styles:
                        filtered_styles.append(style)
                except ValueError:
                    continue
            styles_to_use = filtered_styles if filtered_styles else available_styles
        else:
            styles_to_use = available_styles
        
        # Create configuration
        config = IconConfig(
            output_dir=str(output_dir),
            css_filename=css_filename,
            css_prefix="icon",
            icon_styles=styles_to_use,
            include_size_variants=True,
            size_variants=["16", "24", "32", "48"],
            naming_pattern="prefix_style_icon"
        )
        
        # Create generator instance
        generator = ReactPyIconGenerator(config)
        
        # Generate CSS file with icon filtering
        success = generator.save_css_file(icon_filter=icons)
        
        # Save logs if requested (placeholder for future implementation)
        if save_logs:
            # TODO: Implement logging functionality
            # Could save generation logs, errors, statistics, etc.
            pass
        
        return success
        
    except Exception as e:
        # Silent error handling - no print statements
        return False



def get_icon(icon_name: str, style: str = "filled") -> Optional[str]:
    """
    Quick function to get the base64 data URI of an icon
    
    Args:
        icon_name: Icon name
        style: Icon style
        
    Returns:
        Base64 data URI string or None
    """
    generator = ReactPyIconGenerator()
    return generator.get_icon_base64(icon_name, style)