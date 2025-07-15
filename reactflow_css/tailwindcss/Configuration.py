import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Union, Optional

from .generate import Generator_Config
from .exceptions import TailwindError, ModuleNotFound, ProcessError

generator = Generator_Config()

class configure:
    def __init__(self, __path__):
        self.main_dir = os.path.dirname(os.path.abspath(__path__))
        self.configs = ""
        self.index = ""
        self.path_config = None
        self.path_index = None
        
    def config(self, config_dict: Dict[str, Any] = None, **kwargs) -> str:
        """
        Shortcut function to generate config
    
        Usage:
            config({"content": ["./src/**/*.{js,jsx,ts,tsx}"]})
            config(content=["./src/**/*.{js,jsx,ts,tsx}"], darkMode="class")
        """
        try:
            self.configs = generator.config(config_dict, **kwargs)
            return self.configs
        except Exception as e:
            self.configs = ""
    
    def render_templates(self, path_config: str = None, path_index: str = None) -> None:
        """
        Loads templates from files.
        """
        errors = []
        
        if not path_config:
            path_config = "./tailwind.config.js"
            errors.append("path_config not provided, using default")
        
        if not path_index:
            path_index = "./input.css"
            errors.append("path_index not provided, using default")
        
        try:
            # Validate paths
            validated_paths = validate_paths(self.main_dir, path_config, path_index)
            path_config, path_index = validated_paths
            
            # Store paths for use in other methods
            self.path_config = path_config
            self.path_index = path_index
            
            # Read config file
            if os.path.exists(path_config):
                with open(path_config, "r") as f:
                    self.configs = f.read()
            else:
                f"""Warning: Config file {path_config} not found"""
                self.configs = ""
            
            # Read index file
            if os.path.exists(path_index):
                with open(path_index, "r") as f:
                    self.index = f.read()
            else:
                f"""Warning: Index file {path_index} not found"""
                self.index = ""
                
        except Exception as e:
            raise ProcessError(f"Error reading templates: {e}")
        
        if errors:
            raise ProcessError("Error:", "; ".join(errors))
    
    def default_templates(self, path_output: str = None) -> str:
        current_dir = Path(__file__).parent
        if not path_output.endswith('.css'):
            path_output += "output.css"
        
        template_path = current_dir / '..' / 'tailwindcss' / 'output.css'
        
        with open(template_path, "r") as output:
            if path_output:
                open(path_output, "w").write(output.read())
            
            return output.read()

    def compile(
        self,
        path_config: str = None,
        path_index: str = None,
        path_output: str = "output.css",
        index: str = None,
        *args
    ) -> str:
        """
        Main function to run the Tailwind CSS rendering process.
    
        Returns:
            str: The generated CSS content.
        """
        
        # Use stored paths if available, otherwise use provided paths
        if not path_config:
            path_config = self.path_config or "./tailwind.config.js"
        if not path_index:
            path_index = self.path_index or "./input.css"
        
        # Validate paths
        try:
            validated_paths = validate_paths(self.main_dir, path_config, path_index, path_output)
            path_config, path_index, path_output = validated_paths
        except Exception as e:
            raise ProcessError(f"Path validation failed: {e}")
    
        # Ensure proper file extensions
        if not path_config.endswith('.js'):
            path_config = os.path.join(path_config, "tailwind.config.js")
    
        if not path_index.endswith('.css'):
            path_index = os.path.join(path_index, "input.css")
    
        if not path_output.endswith('.css'):
            path_output = os.path.join(path_output, "output.css")
    
        # Setup default config if none exists
        if not self.configs:
            try:
                if os.path.exists(path_config):
                    with open(path_config, "r") as f:
                        self.configs = f.read()
                
                if not self.configs:
                    self.configs = generator.config({
                        "content": ["./**/*.{js,jsx,ts,tsx,html,py}"]
                    })
            except Exception as e:
                self.configs = generator.config({
                    "content": ["./**/*.{js,jsx,ts,tsx,html,py}"]
                })
        
        # Setup default index CSS if none exists
        if not index:
            index = self.index if self.index else None
            
        if not index:
            try:
                if os.path.exists(path_index):
                    with open(path_index, "r") as f:
                        index = f.read()
                
                if not index:
                    index = "@tailwind base;\n@tailwind components;\n@tailwind utilities;"
            except Exception as e:
                index = "@tailwind base;\n@tailwind components;\n@tailwind utilities;"
    
        # Check Node.js and npm first
        if not check_node_npm():
            raise ModuleNotFound("Node.js or npm not available. Cannot proceed.")
    
        is_installed = check_tailwind()
    
        if not is_installed:
            install_success = installation_tailwindcss()
            
            if not install_success:
                raise ModuleNotFound("Failed to install Tailwind CSS")
    
        # Create directories if they don't exist
        for path in [path_config, path_index, path_output]:
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
    
        try:
            # Write config file
            with open(path_config, "w") as configs_file:
                configs_file.write(self.configs)
            
            # Write index CSS file
            with open(path_index, "w") as index_file:
                index_file.write(index)
        
            # Generate output CSS
            css_generation_success = installation_output_css(
                path_config=path_config, 
                path_index=path_index, 
                path_output=path_output, 
                *args
            )
        
            if css_generation_success:
                # Read and return CSS content
                if os.path.exists(path_output):
                    with open(path_output, "r") as output_file:
                        return output_file.read()
                else:
                    raise ProcessError("CSS file was not generated")
            else:
                raise ProcessError("Failed to generate CSS")
    
        except Exception as e:
            raise ProcessError(f"Error during rendering: {e}")

def validate_paths(__main__, *paths):
    """Validates and normalizes paths."""
    validated_paths = []
    
    for path in paths:
        if not path:
            raise ValueError("Path cannot be empty")
        
        # If path is already absolute, use it as is
        if os.path.isabs(path):
            validated_paths.append(os.path.normpath(path))
        else:
            # Combine with main directory
            normalized_path = os.path.normpath(os.path.join(__main__, path))
            validated_paths.append(normalized_path)
    
    return validated_paths

def check_node_npm():
    """Checks if Node.js and npm are available."""
    try:
        # Check Node.js
        node_result = subprocess.run(
            ['node', '--version'], 
            capture_output=True, 
            text=True, 
            check=False,
            timeout=10
        )
        if node_result.returncode != 0:
            return False
        
        # Check npm
        npm_result = subprocess.run(
            ['npm', '--version'], 
            capture_output=True, 
            text=True, 
            check=False,
            timeout=10
        )
        if npm_result.returncode != 0:
            return False
            
        return True
        
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

def check_tailwind():
    """Checks if tailwindcss is installed."""
    try:
        # Try a simpler command first
        result = subprocess.run(
            ['npx', 'tailwindcss', '--help'], 
            capture_output=True, 
            text=True, 
            check=False,
            timeout=30
        )
        
        if result.returncode == 0:
            return True
        
        # If it fails, try with npm list
        result = subprocess.run(
            ['npm', 'list', 'tailwindcss'], 
            capture_output=True, 
            text=True, 
            check=False,
            timeout=15
        )
        
        if result.returncode == 0 and 'tailwindcss' in result.stdout:
            return True
        
        # Try checking global installation
        result = subprocess.run(
            ['npm', 'list', '-g', 'tailwindcss'], 
            capture_output=True, 
            text=True, 
            check=False,
            timeout=15
        )
        
        if result.returncode == 0 and 'tailwindcss' in result.stdout:
            return True
            
        return False
        
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

def installation_tailwindcss():
    """Installs tailwindcss."""
    try:
        result = subprocess.run(
            ['npm', 'install', 'tailwindcss@latest'], 
            capture_output=True, 
            text=True, 
            check=False,
            timeout=300  # 5 minute timeout for installation
        )
        
        if result.returncode == 0:
            # Check for error messages in stderr
            if 'error' not in result.stderr.lower():
                return True
            else:
                return False
        else:
            return False
        
    except subprocess.TimeoutExpired:
        return False
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        return False
    
def installation_output_css(
    path_config: str = "./tailwind.config.js",
    path_index: str = "./input.css",
    path_output: str = "./output.css",
    *args
) -> bool:
    """Generates output CSS from Tailwind."""
    
    # Default arguments
    default_args = ['--verbose']
    
    if not args:
        args = default_args
    
    try:
        result = subprocess.run(
            ['npx', 'tailwindcss', '-c', path_config, '-i', path_index, '-o', path_output] + list(args), 
            capture_output=True, 
            text=True, 
            check=False,
            timeout=60
        )
        
        if result.returncode == 0:
            return True
        else:
            return False
        
    except subprocess.TimeoutExpired:
        return False
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        return False

def default_css(path_output: str = None) -> str:
    current_dir = Path(__file__).parent
    template_path = current_dir / '..' / 'modules' / 'tailwindcss' / 'output.css'
        
    with open(template_path, "r") as output:
        if path_output:
            open(path_output, "w").write(output.read())
            
        return output.read()
