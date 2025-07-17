import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum
from reactpy import component, html

class IconStyle(Enum):
    """Style ikon yang tersedia"""
    FILLED = "filled"
    OUTLINED = "outlined"
    ROUND = "round"
    SHARP = "sharp"
    TWO_TONE = "two-tone"


@dataclass
class IconConfig:
    """Konfigurasi untuk generator ikon"""
    output_dir: str = "output"
    css_filename: str = "icons.css"
    css_prefix: str = "icon"
    icon_styles: List[IconStyle] = None
    include_size_variants: bool = True
    size_variants: List[str] = None
    
    def __post_init__(self):
        if self.icon_styles is None:
            self.icon_styles = list(IconStyle)
        if self.size_variants is None:
            self.size_variants = ["16", "24", "32", "48"]


class ReactPyIconGenerator:
    """Generator ikon SVG untuk ReactPy dengan CSS background-image"""
    
    def __init__(self, config: Optional[IconConfig] = None):
        self.config = config or IconConfig()
        
        # Path absolut ke package icons directory
        self.package_path = Path(__file__).parent.absolute()
        self.icons_path = self.package_path / "icons"
        
        # Output directory (user-configurable)
        self.output_path = Path(self.config.output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Validate icons directory exists
        if not self.icons_path.exists():
            raise FileNotFoundError(f"Icons directory not found: {self.icons_path}")
    
    def _get_icon_path(self, icon_name: str, style: IconStyle) -> Optional[Path]:
        """Get absolute path to icon file"""
        filename = f"{icon_name}.svg"
        icon_path = self.icons_path / style.value / filename
        return icon_path if icon_path.exists() else None
    
    def _scan_available_icons(self) -> Dict[str, List[str]]:
        """Scan semua ikon yang tersedia dalam package"""
        catalog = {}
        
        for style in self.config.icon_styles:
            style_path = self.icons_path / style.value
            if not style_path.exists():
                continue
            
            icons = []
            for svg_file in style_path.glob("*.svg"):
                icon_name = svg_file.stem
                if icon_name not in icons:
                    icons.append(icon_name)
            
            catalog[style.value] = sorted(icons)
        
        return catalog
    
    def _generate_css_rule(self, icon_name: str, style: IconStyle, size: Optional[str] = None) -> Optional[str]:
        """Generate CSS rule untuk single icon"""
        icon_path = self._get_icon_path(icon_name, style)
        if not icon_path:
            return None
        
        # CSS class name
        class_name = f".{self.config.css_prefix}-{style.value}-{icon_name.replace('_', '-')}"
        if size:
            class_name += f"-{size}"
        
        # Generate CSS dengan url() function
        css_rule = f"{class_name} {{\n"
        css_rule += f"    background-image: url('{self.get_icon_path(icon_path)}');\n"
        css_rule += f"    background-repeat: no-repeat;\n"
        css_rule += f"    background-position: center;\n"
        css_rule += f"    background-size: contain;\n"
        css_rule += f"    display: inline-block;\n"
        css_rule += f"    width: {size}px;\n" if size else f"    width: 24px;\n"
        css_rule += f"    height: {size}px;\n" if size else f"    height: 24px;\n"
        css_rule += f"}}"
        
        return css_rule
    
    def get_icon_path(self, icon_name: str, style: Union[str, IconStyle] = IconStyle.FILLED) -> Optional[str]:
        """
        Get file path untuk ReactPy component
        
        Args:
            icon_name: Nama ikon
            style: Style ikon
            
        Returns:
            File path string atau None
        """
        if isinstance(style, str):
            try:
                style = IconStyle(style)
            except ValueError:
                return None
        
        icon_path = self._get_icon_path(icon_name, style)
        if icon_path:
            return str(icon_path)
        
        return None
    
    def generate_css_file(self, icon_filter: Optional[List[str]] = None) -> str:
        """
        Generate CSS file untuk semua ikon
        
        Args:
            icon_filter: Filter ikon yang akan di-generate
            
        Returns:
            CSS content string
        """
        catalog = self._scan_available_icons()
        css_rules = []
        
        # CSS Header
        css_rules.append("/* ReactPy Icon Generator - Auto Generated */")
        css_rules.append("/* Base icon styles */")
        css_rules.append(f"[class^=\"{self.config.css_prefix}-\"] {{")
        css_rules.append("    display: inline-block;")
        css_rules.append("    background-repeat: no-repeat;")
        css_rules.append("    background-position: center;")
        css_rules.append("    background-size: contain;")
        css_rules.append("}")
        css_rules.append("")
        
        # Generate rules untuk setiap ikon
        for style in self.config.icon_styles:
            if style.value not in catalog:
                continue
            
            available_icons = catalog[style.value]
            target_icons = icon_filter if icon_filter else available_icons
            
            for icon_name in target_icons:
                if icon_name not in available_icons:
                    continue
                
                # Default size
                rule = self._generate_css_rule(icon_name, style)
                if rule:
                    css_rules.append(rule)
                
                # Size variants
                if self.config.include_size_variants:
                    for size in self.config.size_variants:
                        rule = self._generate_css_rule(icon_name, style, size)
                        if rule:
                            css_rules.append(rule)
        
        return '\n\n'.join(css_rules)
    
    def save_css_file(self, icon_filter: Optional[List[str]] = None) -> bool:
        """Save CSS file ke disk"""
        try:
            css_content = self.generate_css_file(icon_filter)
            css_path = self.output_path / self.config.css_filename
            
            with css_path.open('w', encoding='utf-8') as f:
                f.write(css_content)
            
            print(f"CSS file saved: {css_path}")
            return True
            
        except Exception as e:
            print(f"Error saving CSS file: {e}")
            return False
    
    def get_available_icons(self) -> Dict[str, List[str]]:
        """Get list semua ikon yang tersedia"""
        return self._scan_available_icons()
    
    def build(self, icon_filter: Optional[List[str]] = None) -> Dict:
        """
        Build CSS dan return hasil
        
        Args:
            icon_filter: Filter ikon yang akan di-build
            
        Returns:
            Dictionary hasil build
        """
        result = {
            'success': False,
            'css_file': None,
            'available_icons': {},
            'total_icons': 0
        }
        
        try:
            # Generate CSS
            success = self.save_css_file(icon_filter)
            if success:
                result['css_file'] = str(self.output_path / self.config.css_filename)
            
            # Get available icons
            available_icons = self.get_available_icons()
            result['available_icons'] = available_icons
            result['total_icons'] = sum(len(icons) for icons in available_icons.values())
            result['success'] = success
            
        except Exception as e:
            print(f"Build error: {e}")
        
        return result


# ReactPy Helper Functions
def create_icon_generator(output_dir: str = "output", css_prefix: str = "icon", **kwargs) -> ReactPyIconGenerator:
    """
    Helper untuk membuat generator dengan konfigurasi mudah
    
    Args:
        output_dir: Direktori output
        css_prefix: Prefix untuk CSS class
        **kwargs: Parameter tambahan
        
    Returns:
        ReactPyIconGenerator instance
    """
    config = IconConfig(
        output_dir=output_dir,
        css_prefix=css_prefix,
        **kwargs
    )
    return ReactPyIconGenerator(config)


def get_icon(icon_name: str, style: str = "filled") -> Optional[str]:
    """
    Quick function untuk mendapatkan path file ikon
    
    Args:
        icon_name: Nama ikon
        style: Style ikon
        
    Returns:
        Path file string atau None
    """
    generator = ReactPyIconGenerator()
    return generator.get_icon_path(icon_name, style)
