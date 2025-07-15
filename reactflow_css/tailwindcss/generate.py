import json
import os
from typing import Dict, Any, List, Union

class Generator_Config:
    def __init__(self):
        # List of all valid Tailwind CSS configurations
        self.valid_config_keys = {
            'content', 'theme', 'plugins', 'presets', 'darkMode', 'prefix', 
            'important', 'separator', 'corePlugins', 'safelist', 'blocklist',
            'future', 'experimental'
        }
        
        # List of valid theme configurations
        self.valid_theme_keys = {
            'screens', 'colors', 'spacing', 'animation', 'keyframes', 'aspectRatio',
            'backdropBlur', 'backdropBrightness', 'backdropContrast', 'backdropGrayscale',
            'backdropHueRotate', 'backdropInvert', 'backdropOpacity', 'backdropSaturate',
            'backdropSepia', 'backgroundColor', 'backgroundImage', 'backgroundOpacity',
            'backgroundPosition', 'backgroundSize', 'blur', 'brightness', 'borderColor',
            'borderOpacity', 'borderRadius', 'borderWidth', 'boxShadow', 'boxShadowColor',
            'caretColor', 'accentColor', 'contrast', 'container', 'content', 'cursor',
            'divideColor', 'divideOpacity', 'divideWidth', 'dropShadow', 'fill', 'flex',
            'flexBasis', 'flexGrow', 'flexShrink', 'fontFamily', 'fontSize', 'fontWeight',
            'gap', 'gradientColorStops', 'grayscale', 'gridAutoColumns', 'gridAutoRows',
            'gridColumn', 'gridColumnEnd', 'gridColumnStart', 'gridRow', 'gridRowEnd',
            'gridRowStart', 'gridTemplateColumns', 'gridTemplateRows', 'height', 'hueRotate',
            'inset', 'invert', 'isolation', 'letterSpacing', 'lineHeight', 'listStyleType',
            'margin', 'maxHeight', 'maxWidth', 'minHeight', 'minWidth', 'objectPosition',
            'opacity', 'order', 'padding', 'placeholderColor', 'placeholderOpacity',
            'ringColor', 'ringOffsetColor', 'ringOffsetWidth', 'ringOpacity', 'ringWidth',
            'rotate', 'saturate', 'scale', 'scrollMargin', 'scrollPadding', 'sepia',
            'skew', 'space', 'stroke', 'strokeWidth', 'textColor', 'textDecorationColor',
            'textDecorationThickness', 'textIndent', 'textOpacity', 'textUnderlineOffset',
            'transformOrigin', 'transitionDelay', 'transitionDuration', 'transitionProperty',
            'transitionTimingFunction', 'translate', 'width', 'willChange', 'zIndex'
        }

    def _convert_value_to_js(self, value: Any, indent_level: int = 0) -> str:
        """Converts Python values to JavaScript format"""
        indent = "  " * indent_level
        
        if isinstance(value, dict):
            if not value:
                return "{}"
            
            lines = ["{"]
            for key, val in value.items():
                # Fix key handling - use quotes for keys containing special characters
                if key.replace('_', '').replace('-', '').replace('.', '').isalnum():
                    js_key = key
                else:
                    js_key = f"'{key}'"
                
                js_val = self._convert_value_to_js(val, indent_level + 1)
                lines.append(f"{indent}  {js_key}: {js_val},")
            lines.append(f"{indent}}}")
            return "\n".join(lines)
        
        elif isinstance(value, list):
            if not value:
                return "[]"
            
            if all(isinstance(item, (str, int, float, bool)) for item in value):
                # Simple array on one line
                js_items = [self._convert_value_to_js(item) for item in value]
                return f"[{', '.join(js_items)}]"
            else:
                # Complex array with multiple lines
                lines = ["["]
                for item in value:
                    js_item = self._convert_value_to_js(item, indent_level + 1)
                    lines.append(f"{indent}  {js_item},")
                lines.append(f"{indent}]")
                return "\n".join(lines)
        
        elif isinstance(value, str):
            # Handle special JavaScript expressions
            if value.startswith("require(") or value.startswith("import(") or value.startswith("plugin("):
                return value
            elif "'" in value and '"' not in value:
                return f'"{value}"'
            else:
                # Escape single quotes in string
                escaped_value = value.replace("'", "\'")
                return f"'{escaped_value}'"
        
        elif isinstance(value, bool):
            return "true" if value else "false"
        
        elif value is None:
            return "null"
        
        elif isinstance(value, (int, float)):
            return str(value)
        
        else:
            # Fallback for other data types
            return f"'{str(value)}'"

    def _validate_config(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Validates and cleans the configuration"""
        if not isinstance(config_dict, dict):
            return {}
            
        validated = {}
        
        for key, value in config_dict.items():
            # Validate top-level keys
            if key in self.valid_config_keys:
                if key == 'theme' and isinstance(value, dict):
                    # Validate theme keys
                    validated_theme = {}
                    for theme_key, theme_value in value.items():
                        if theme_key in self.valid_theme_keys or theme_key == 'extend':
                            validated_theme[theme_key] = theme_value
                        else:
                            f"""Warning: Unknown theme key '{theme_key}' will be included"""
                            validated_theme[theme_key] = theme_value
                    validated[key] = validated_theme
                else:
                    validated[key] = value
            else:
                f"""Warning: Unknown config key '{key}' will be included"""
                validated[key] = value
                
        return validated

    def config(self, config_dict: Dict[str, Any] = None, **kwargs) -> str:
        """
        Generate tailwind.config.js content
        
        Args:
            config_dict: Dictionary berisi konfigurasi Tailwind
            **kwargs: Konfigurasi tambahan sebagai keyword arguments
            
        Returns:
            String berisi konten tailwind.config.js
        """
        # Gabungkan config_dict dan kwargs
        final_config = {}
        
        if config_dict and isinstance(config_dict, dict):
            final_config.update(config_dict)
        
        if kwargs:
            final_config.update(kwargs)
        
        # Validate configuration
        validated_config = self._validate_config(final_config)
        
        # Generate JavaScript string
        if not validated_config:
            return "/** @type {import('tailwindcss').Config} */\nmodule.exports = {\n  content: [],\n  theme: {\n    extend: {},\n  },\n  plugins: [],\n}"
        
        js_content = self._convert_value_to_js(validated_config)
        
        # Format final output
        config_string = f"/** @type {{import('tailwindcss').Config}} */\nmodule.exports = {js_content}"
        
        return config_string