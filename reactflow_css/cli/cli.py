#!/usr/bin/env python3
"""
rf-css - ReactFlow-CSS CLI Tool
A command-line interface for TailwindCSS and SASS/SCSS conversion utilities
"""

import sys
import ast
import subprocess
import threading
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Get main directory path
MAIN_DIRS = Path(__file__).parent
NODE_MODULES_PATH = MAIN_DIRS / 'node_modules' / '.bin' / 'tailwindcss'


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def red(text: str) -> str:
        """Apply red color to text"""
        return f"{Colors.RED}{text}{Colors.RESET}"
    
    @staticmethod
    def green(text: str) -> str:
        """Apply green color to text"""
        return f"{Colors.GREEN}{text}{Colors.RESET}"
    
    @staticmethod
    def yellow(text: str) -> str:
        """Apply yellow color to text"""
        return f"{Colors.YELLOW}{text}{Colors.RESET}"
    
    @staticmethod
    def blue(text: str) -> str:
        """Apply blue color to text"""
        return f"{Colors.BLUE}{text}{Colors.RESET}"
    
    @staticmethod
    def cyan(text: str) -> str:
        """Apply cyan color to text"""
        return f"{Colors.CYAN}{text}{Colors.RESET}"
    
    @staticmethod
    def bold(text: str) -> str:
        """Apply bold formatting to text"""
        return f"{Colors.BOLD}{text}{Colors.RESET}"


class LoadingSpinner:
    """Thread-safe loading spinner for CLI operations"""
    
    def __init__(self, message: str = "Loading", spinner_type: str = "dots"):
        """
        Initialize loading spinner
        
        Args:
            message: Message to display with spinner
            spinner_type: Type of spinner animation
        """
        self.message = message
        self.is_spinning = False
        self.spinner_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Different spinner types
        self.spinners = {
            "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
            "circle": ["◐", "◓", "◑", "◒"],
            "snake": ["⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈"],
            "bouncing": ["⠁", "⠂", "⠄", "⠂"],
            "pulsing": ["●", "◉", "○", "◉"]
        }
        
        self.current_spinner = self.spinners.get(spinner_type, self.spinners["dots"])
        
    def _spin(self) -> None:
        """Internal method to handle the spinning animation"""
        index = 0
        while self.is_spinning:
            with self._lock:
                if not self.is_spinning:
                    break
                print(f"\r{self.current_spinner[index]} {self.message}", end="", flush=True)
            index = (index + 1) % len(self.current_spinner)
            time.sleep(0.1)  # 100ms delay for smooth animation
            
    def start(self) -> None:
        """Start the loading spinner"""
        with self._lock:
            if not self.is_spinning:
                self.is_spinning = True
                self.spinner_thread = threading.Thread(target=self._spin, daemon=True)
                self.spinner_thread.start()
            
    def stop(self, success_message: Optional[str] = None, error_message: Optional[str] = None) -> None:
        """
        Stop the loading spinner
        
        Args:
            success_message: Message to display on success
            error_message: Message to display on error
        """
        with self._lock:
            if self.is_spinning:
                self.is_spinning = False
                
        if self.spinner_thread and self.spinner_thread.is_alive():
            self.spinner_thread.join(timeout=1.0)
        
        # Clear the spinner line
        print(f"\r{' ' * (len(self.message) + 5)}", end="", flush=True)
        print("\r", end="", flush=True)
        
        # Print final message
        if success_message:
            print(Colors.green(f"[SUCCESS] {success_message}"))
        elif error_message:
            print(Colors.red(f"[ERROR] {error_message}"))
                
    def update_message(self, new_message: str) -> None:
        """Update the spinner message"""
        with self._lock:
            self.message = new_message


class CommandExecutor:
    """Handle subprocess command execution with proper error handling"""
    
    @staticmethod
    def run_command_with_spinner(
        command: List[str], 
        message: str, 
        timeout: int = 30, 
        spinner_type: str = "dots"
    ) -> Optional[subprocess.CompletedProcess]:
        """
        Run a subprocess command with a loading spinner
        
        Args:
            command: Command to execute as list of strings
            message: Message to display during execution
            timeout: Command timeout in seconds
            spinner_type: Type of spinner animation
            
        Returns:
            CompletedProcess object or None if failed
        """
        spinner = LoadingSpinner(message, spinner_type)
        
        try:
            spinner.start()
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
                encoding='utf-8'
            )
            
            spinner.stop()
            return result
            
        except subprocess.TimeoutExpired:
            spinner.stop(error_message=f"Command timed out after {timeout} seconds")
            logger.error(f"Command timeout: {' '.join(command)}")
            return None
        except FileNotFoundError as e:
            spinner.stop(error_message=f"Command not found: {e}")
            logger.error(f"Command not found: {' '.join(command)}")
            return None
        except Exception as e:
            spinner.stop(error_message=f"Command failed: {str(e)}")
            logger.error(f"Command execution failed: {e}")
            return None

    @staticmethod
    def run_command_simple(
        command: List[str], 
        timeout: int = 10
    ) -> Optional[subprocess.CompletedProcess]:
        """
        Run a simple command without spinner (for help commands)
        
        Args:
            command: Command to execute as list of strings
            timeout: Command timeout in seconds
            
        Returns:
            CompletedProcess object or None if failed
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
                encoding='utf-8'
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {' '.join(command)}")
            return None
        except FileNotFoundError:
            logger.error(f"Command not found: {' '.join(command)}")
            return None
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return None


class PathValidator:
    """Validate and sanitize file paths"""
    
    @staticmethod
    def validate_output_path(path: str) -> bool:
        """
        Validate output path format
        
        Args:
            path: Path string to validate
            
        Returns:
            True if path is valid, False otherwise
        """
        if not path:
            return False
            
        if not path.startswith('./'):
            print(Colors.red(f"[ERROR] Path must start with './' - got '{path}'"))
            return False
            
        # Check for path traversal attempts
        if '..' in path:
            print(Colors.red(f"[ERROR] Path traversal not allowed - got '{path}'"))
            return False
            
        return True
    
    @staticmethod
    def ensure_directory_exists(path: str) -> bool:
        """
        Ensure directory exists for given file path
        
        Args:
            path: File path string
            
        Returns:
            True if directory exists or was created, False otherwise
        """
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory for {path}: {e}")
            return False


class DependencyChecker:
    """Check for required dependencies"""
    
    @staticmethod
    def check_node_dependency() -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(
                ['node', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @staticmethod
    def check_tailwindcss_binary() -> bool:
        """Check if TailwindCSS binary exists"""
        return NODE_MODULES_PATH.exists()


def show_help() -> None:
    """Display help information"""
    help_text = """
Usage: rf-css [--verbose] [--version] command [arguments]

A comprehensive CLI tool for managing CSS workflows in ReactFlow projects.
Integrates TailwindCSS compilation, SASS/SCSS conversion, and Material Icons generation.
  --verbose enables detailed output with comprehensive information and error traces
  --version displays current tool version

Commands:

  tailwindcss [args]   - Access TailwindCSS CLI functionality directly with
                         full feature support including configuration
                         management and utility generation.

  sass-convert [args]  - Convert SASS/SCSS files to CSS with advanced
                         compilation options, source mapping, and
                         directory processing capabilities.

  generate-icons [args] - Generate CSS for Material Icons with URL-based
                          icon integration for ReactFlow components.

Global Arguments:

  -i, --input <path>   - Specify input file path for processing. Used
                         by sass-convert and other file-based commands.

  -o, --output <path>  - Specify output file path for generated content.
                         Defaults vary by command context.

  -h, --help           - Display this help message with complete command
                         reference and usage examples.

  --tailwindcss-help   - Display comprehensive TailwindCSS CLI help with
                         all available options and configurations.

  --sass-convert-help  - Display detailed SASS/SCSS conversion help with
                         advanced options, examples, and best practices.

TailwindCSS Specific Arguments:

  -c, --config <path>  - Specify custom TailwindCSS configuration file
                         path. Defaults to 'tailwind.config.js' in
                         current directory.

  --default <path>     - Generate default TailwindCSS base styles and
                         utilities to specified output path for quick
                         project initialization.

SASS/SCSS Specific Arguments:

  --directory <path>   - Specify input directory containing SASS/SCSS
                         files for batch processing. Supports nested
                         directory structures.

  -s, --style <format> - Set CSS output formatting style. Available
                         formats: expanded, compressed, compact, nested.
                         Default is 'expanded'.

  --source-map         - Generate corresponding source map files (.css.map)
                         for debugging and development workflow
                         integration.

  --recursive          - Enable recursive scanning of subdirectories when
                         processing directories. Processes all SASS/SCSS
                         files in directory tree.

  --watch              - Enable watch mode for automatic recompilation
                         when source files change. Ideal for development
                         workflow.

  --glob <pattern>     - Use glob pattern to match multiple files with
                         specific naming conventions or locations.
                         Example: '**/*.scss'

  --include-path <path> - Specify additional directories where SASS can
                          find imported files and dependencies. Supports
                          multiple paths.

  --precision <number> - Set decimal precision for numeric values in CSS
                         output. Controls rounding of calculated values.
                         Default is 5 decimal places.

Generate-Icons Specific Arguments:

  --logs <boolean>     - Enable generation logs with detailed processing
                         information. Accepts true/false values.
                         Default is false.

  --all                - Generate CSS for all available Material Icons
                         across all supported styles. Can be combined
                         with --type for filtered generation.

  --icon <json_array>  - Specify exact icon names to generate. Accepts
                         JSON array format with valid Material Icon
                         names. Example: '["home", "search", "menu"]'

  --type <json_array>  - Specify icon styles to generate. Accepts JSON
                         array with available types. Supported types:
                         filled, outlined, round, sharp, two-tone.

Available Icon Types:

  filled               - Solid icons with filled interior areas for
                         strong visual emphasis and primary actions.

  outlined             - Line-based icons with transparent interiors
                         for subtle interface elements and secondary
                         actions.

  round                - Icons with rounded corners and soft edges for
                         friendly, approachable interface design.

  sharp                - Icons with angular corners and sharp edges for
                         modern, technical interface aesthetics.

  two-tone             - Dual-color icons using primary and secondary
                         colors for enhanced visual hierarchy and depth.

Examples:

  rf-css tailwindcss init --default ./styles.css
                       Initialize new project with default TailwindCSS
                       base styles and utilities.

  rf-css tailwindcss -c ./config/tailwind.config.js -i ./src/input.css -o ./dist/output.css
                       Compile TailwindCSS with custom configuration
                       and specific input/output paths.

  rf-css sass-convert -i ./styles.scss -o ./dist/styles.css --style compressed
                       Convert single SCSS file to compressed CSS
                       format for production deployment.

  rf-css sass-convert --directory ./src/scss --recursive --watch -o ./dist/css
                       Watch entire SCSS directory tree for changes
                       and automatically recompile to output directory.

  rf-css sass-convert -i ./main.scss --source-map --include-path ./vendors --precision 3
                       Convert SCSS with source mapping, custom import
                       paths, and specific numeric precision.

  rf-css generate-icons --all --type '["filled", "outlined"]' -o ./icons.css
                       Generate all Material Icons in filled and
                       outlined styles only.

  rf-css generate-icons --icon '["home", "search", "settings"]' --logs true
                       Generate specific icons with detailed logging
                       enabled for debugging.

  rf-css --sass-convert-help
                       Display comprehensive SASS conversion help with
                       advanced configuration options.

  rf-css --verbose generate-icons --all
                       Generate all icons with detailed verbose output
                       showing processing steps and results.

Notes:

  • This tool is currently in beta - report issues and provide feedback
  • File paths should be relative (starting with './') or absolute paths
  • JSON array arguments must be properly quoted to prevent shell interpretation
  • Watch mode requires manual termination (Ctrl+C) to stop monitoring
  • Source maps are recommended for development but should be excluded from production
  • Icon generation creates CSS classes compatible with ReactFlow component integration
  • TailwindCSS commands require proper configuration file for advanced features
  • SASS/SCSS processing supports both Dart Sass and LibSass syntax variations
    """
    print(help_text)


def generate_default_css(output_path: str) -> bool:
    """
    Generate default TailwindCSS file
    
    Args:
        output_path: Path where to write the default CSS
        
    Returns:
        True if successful, False otherwise
    """
    if not PathValidator.validate_output_path(output_path):
        return False
    
    if not PathValidator.ensure_directory_exists(output_path):
        return False
    
    try:
        spinner = LoadingSpinner("Generating default Tailwind CSS...", "bouncing")
        spinner.start()
        
        time.sleep(1)  # Small delay to show the spinner
        
        # Import here to avoid import errors if module doesn't exist
        try:
            from ..tailwindcss.Configuration import default_css
        except ImportError:
            spinner.stop(error_message="TailwindCSS configuration module not found")
            return False
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(default_css())
        
        spinner.stop(success_message=f"Default CSS written to {output_path}")
        return True
        
    except Exception as e:
        if 'spinner' in locals():
            spinner.stop(error_message=f"Error writing default CSS: {e}")
        logger.error(f"Failed to generate default CSS: {e}")
        return False


def run_tailwind_cli(args: List[str]) -> int:
    """
    Execute TailwindCSS CLI commands
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Check dependencies
    if not DependencyChecker.check_node_dependency():
        print(Colors.red("[ERROR] Node.js is required but not found"))
        return 1
    
    if not DependencyChecker.check_tailwindcss_binary():
        print(Colors.red("[ERROR] TailwindCSS binary not found"))
        return 1
    
    # Default to help if no args provided
    if not args:
        args = ["--help"]
    
    try:
        node_binary_path = str(NODE_MODULES_PATH)
        
        # Handle special cases
        if '--help' in args or '-h' in args:
            # For help commands, no need for spinner
            result = CommandExecutor.run_command_simple(
                ['node', node_binary_path] + args,
                timeout=10
            )
        elif len(args) >= 2 and args[0] == 'init' and args[1] == '--default':
            # Handle default CSS generation
            try:
                output_path = args[2] if len(args) > 2 else "./output.css"
            except IndexError:
                output_path = "./output.css"
            
            success = generate_default_css(output_path)
            return 0 if success else 1
        else:
            # Use spinner for other tailwind commands
            result = CommandExecutor.run_command_with_spinner(
                ['node', node_binary_path] + args,
                f"Running tailwindcss {' '.join(args)}...",
                timeout=60,
                spinner_type="circle"
            )
        
        if not result:
            return 1
            
        # Display output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        return result.returncode
        
    except Exception as e:
        print(Colors.red(f"[ERROR] Error running tailwindcss: {e}"), file=sys.stderr)
        logger.error(f"TailwindCSS execution failed: {e}")
        return 1


def sass_convert_help() -> None:
    """Display SASS convert help information"""
    try:
        from .sass_to_css import ArgumentParser
        parser = ArgumentParser()
        parser.print_help()
    except ImportError:
        print(Colors.red("[ERROR] SASS converter module not found"))


def sass_convert(args: List[str]) -> int:
    """
    Handle sass-convert command with arguments
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        from .sass_to_css import ArgumentParser, SassConverter
    except ImportError:
        print(Colors.red("[ERROR] SASS converter module not found"))
        return 1
    
    parser = ArgumentParser()
    
    try:
        parsed_args = parser.parse_args(args)
        
        if parser.help_requested:
            parser.print_help()
            return 0
        
    except ValueError as e:
        print(Colors.red(f"[ERROR] {e}"))
        print(Colors.yellow("[WARNING] Use 'rf-css --sass-convert-help' for usage information"))
        return 1
    
    converter = SassConverter()
    
    # Setup compilation options
    compile_options = {
        'output_style': parsed_args['style'],
        'source_map': parsed_args['source_map'],
        'include_paths': parsed_args['include_paths'] if parsed_args['include_paths'] else None,
        'precision': parsed_args['precision']
    }
    
    try:
        success = False
        
        if parsed_args['input']:
            # Single file mode
            success = converter.compile_file(
                parsed_args['input'], 
                parsed_args['output'], 
                **compile_options
            )
            if success:
                print(Colors.green("[SUCCESS] SASS/SCSS compilation completed"))
            else:
                print(Colors.red("[ERROR] SASS/SCSS compilation failed"))
            
        elif parsed_args['directory']:
            if parsed_args['watch']:
                # Watch mode
                print(Colors.cyan("[INFO] Starting watch mode..."))
                converter.watch_directory(
                    parsed_args['directory'], 
                    parsed_args['output'], 
                    recursive=parsed_args['recursive'], 
                    **compile_options
                )
                success = True  # Watch mode runs indefinitely
            else:
                # Directory mode
                success = converter.compile_directory(
                    parsed_args['directory'], 
                    parsed_args['output'],
                    recursive=parsed_args['recursive'], 
                    **compile_options
                )
                if success:
                    print(Colors.green("[SUCCESS] Directory compilation completed"))
                else:
                    print(Colors.red("[ERROR] Directory compilation failed"))
                
        elif parsed_args['glob']:
            # Glob pattern mode
            import glob
            files = glob.glob(parsed_args['glob'], recursive=True)
            
            if not files:
                print(Colors.yellow(f"[WARNING] No files found matching pattern: {parsed_args['glob']}"))
                return 0
            
            output_dir = Path(parsed_args['output']) if parsed_args['output'] else Path.cwd()
            success_count = 0
            
            for file_path in files:
                file_path = Path(file_path)
                if file_path.suffix in converter.supported_extensions:
                    if file_path.name.startswith('_'):
                        continue  # Skip partials
                    
                    output_path = output_dir / file_path.with_suffix('.css').name
                    if converter.compile_file(str(file_path), str(output_path), **compile_options):
                        success_count += 1
            
            print(Colors.green(f"[SUCCESS] Glob processing completed: {success_count}/{len(files)} files compiled successfully"))
            success = success_count > 0
        
        return 0 if success else 1
    
    except KeyboardInterrupt:
        print(Colors.yellow("\n[WARNING] SASS conversion interrupted by user"))
        return 130
    except Exception as e:
        print(Colors.red(f"[ERROR] SASS conversion failed: {e}"))
        if parsed_args.get('verbose'):
            import traceback
            traceback.print_exc()
        logger.error(f"SASS conversion failed: {e}")
        return 1


def parse_list_argument(args: List[str], target: str) -> Union[List[Any], None]:
    """
    Extract and parse list arguments safely
    
    Args:
        args: List of command arguments
        target: Target argument to extract
        
    Returns:
        Parsed list or None if error/not found
    """
    try:
        if target not in args:
            return None
            
        index = args.index(target)
        if index + 1 >= len(args):
            print(Colors.red(f"[ERROR] Missing value for argument '{target}'"))
            return None
            
        raw_value = args[index + 1]
        parsed_value = ast.literal_eval(raw_value)
        
        if not isinstance(parsed_value, list):
            print(Colors.red(f"[ERROR] Argument '{target}' must be a list, got: {type(parsed_value).__name__}"))
            return None
            
        return parsed_value
        
    except (ValueError, SyntaxError) as e:
        print(Colors.red(f"[ERROR] Invalid syntax for argument '{target}': {raw_value}"))
        print(Colors.yellow(f"[HINT] Use proper list syntax like: {target} '[\"item1\", \"item2\"]'"))
        return None
    except Exception as e:
        print(Colors.red(f"[ERROR] Failed to parse argument '{target}': {str(e)}"))
        return None


def parse_string_argument(args: List[str], target: str, default_value: str = "") -> str:
    """
    Extract string arguments safely
    
    Args:
        args: List of command arguments
        target: Target argument to extract
        default_value: Default value if not found
        
    Returns:
        Parsed string value or default
    """
    try:
        if target not in args:
            return default_value
            
        index = args.index(target)
        if index + 1 >= len(args):
            print(Colors.red(f"[ERROR] Missing value for argument '{target}'"))
            return default_value
            
        return args[index + 1]
        
    except Exception as e:
        print(Colors.red(f"[ERROR] Failed to parse argument '{target}': {str(e)}"))
        return default_value


def parse_boolean_argument(args: List[str], target: str, default_value: bool = False) -> bool:
    """
    Extract boolean arguments safely
    
    Args:
        args: List of command arguments
        target: Target argument to extract
        default_value: Default value if not found
        
    Returns:
        Parsed boolean value or default
    """
    try:
        if target not in args:
            return default_value
            
        index = args.index(target)
        if index + 1 >= len(args):
            # If no value provided, treat as True (flag-style)
            return True
            
        raw_value = args[index + 1].lower()
        if raw_value in ['true', '1', 'yes', 'on']:
            return True
        elif raw_value in ['false', '0', 'no', 'off']:
            return False
        else:
            # If not a clear boolean, treat as flag
            return True
            
    except Exception as e:
        print(Colors.red(f"[ERROR] Failed to parse boolean argument '{target}': {str(e)}"))
        return default_value


def help_generate_icon() -> None:
    """Display help for generate-icons command"""
    help_text = """
Usage: rf-css [--logs] command [arguments]

A CLI tool for generating CSS from Material Icons for ReactFlow components.
  --logs enables detailed logging for all operations

Commands:

  generate-icons       - Generate CSS for Material Icons with customizable
                         output and filtering options.

Arguments for generate-icons:

  -o, --output <path>  - Specify output CSS file path. Defaults to
                         './output.css' in current directory.

  --all               - Generate CSS for all available Material Icons
                         across all styles. Can be combined with --type
                         to limit styles, or used alone for complete
                         generation.

  --icon <json_array> - Generate CSS for specific icons only. Accepts
                         JSON array format with icon names.
                         Example: '["home", "search", "menu"]'

  --type <json_array> - Generate CSS for specific Material Icon styles
                         only. Accepts JSON array format with style names.
                         Example: '["filled", "outlined"]'

Available Icon Types:

  filled              - Material Icons filled style - solid icons with
                         filled interior areas.

  outlined            - Material Icons outlined style - line-based icons
                         with transparent interior areas.

  round               - Material Icons rounded style - icons with rounded
                         corners and edges for softer appearance.

  sharp               - Material Icons sharp style - icons with sharp,
                         angular corners for modern look.

  two-tone            - Material Icons two-tone style - icons using two
                         colors for depth and visual hierarchy.

Examples:

  rf-css generate-icons --all
                       Generate CSS for all available Material Icons
                       across all five styles.

  rf-css generate-icons --icon '["home", "search"]' -o ./icons.css
                       Generate CSS only for home and search icons,
                       save to icons.css file.

  rf-css generate-icons --icon '["menu"]' --type '["filled", "outlined"]'
                       Generate CSS for menu icon in both filled and
                       outlined styles only.

  rf-css generate-icons --all --type '["filled"]' --logs -o ./filled-icons.css
                       Generate all icons in filled style only with
                       detailed logging enabled.

  rf-css generate-icons --type '["outlined", "round"]' --logs
                       Generate all icons in outlined and round styles
                       with logging, output to default file.

Notes:

  • Icon and type arguments must be valid JSON array format enclosed in quotes
  • Output path should be relative (starting with './') or absolute path
  • Use single or double quotes around JSON arrays to prevent shell interpretation
  • The --all flag can be combined with --type to generate all icons of specific styles
  • Logging is disabled by default; use --logs flag to enable detailed output
  • Generated CSS includes all necessary classes for ReactFlow icon integration
    """
    print(help_text)


def generate_icons(args: List[str]) -> int:
    """
    Handle generate-icons command with improved argument parsing
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Import the icon generation module
        from ..icons.generate import create_icon_generator
    except ImportError:
        print(Colors.red("[ERROR] Icon generation module not found"))
        return 1
    
    # Show help if no arguments or help requested
    if not args or '--help' in args or '-h' in args:
        help_generate_icon()
        return 0
    
    # Parse arguments with improved error handling
    output_path = parse_string_argument(args, '-o', './output.css')
    if not output_path.startswith('./'):
        output_path = './' + output_path
    
    save_logs = parse_boolean_argument(args, '--logs', False)
    icon_list = parse_list_argument(args, '--icon')
    icon_types = parse_list_argument(args, '--type')
    
    # Validate output path
    if not PathValidator.validate_output_path(output_path):
        return 1
    
    if not PathValidator.ensure_directory_exists(output_path):
        print(Colors.red(f"[ERROR] Cannot create directory for output path: {output_path}"))
        return 1
    
    try:
        # Execute icon generation based on provided arguments
        if '--all' in args:
            if (not icon_list) ^ (not icon_types):  # Empty list
                print(Colors.yellow("[WARNING] Icon list or icon type is empty, no icons to generate"))
                return 0
                
            print(Colors.cyan("[INFO] Generating all available icons..."))
            create_icon_generator(
                output_path=output_path,
                save_logs=save_logs,
                icon_filter=icon_types,
                icons=icon_list
            )
            print(Colors.green(f"[SUCCESS] All {icon_list or icon_types or (icon_list, icon_types) or ""} icons generated successfully in {output_path}"))
            
        else:
            if not icon_list or not icon_types:  # Empty list
                print(Colors.yellow("[WARNING] Icon list and icon type is empty, no icons to generate"))
                return 0
                
            print(Colors.cyan(f"[INFO] Generating {len(icon_list)} specific icons..."))
            create_icon_generator(
                output_path=output_path,
                save_logs=save_logs,
                icon_filter=icon_types,
                icons=icon_list
            )
            print(Colors.green(f"[SUCCESS] Icons {icon_list} with {icon_types} generated successfully in {output_path}"))
            
        return 0
        
    except Exception as e:
        print(Colors.red(f"[ERROR] Icon generation failed: {str(e)}"))
        print(Colors.yellow("[HINT] Use 'rf-css generate-icons --help' for usage information"))
        logger.error(f"Icon generation error: {e}")
        return 1


def get_version() -> str:
    """
    Get application version
    
    Returns:
        Version string or error message
    """
    try:
        from ..__init__ import __version__
        return __version__
    except ImportError:
        return "Version information not available"


def handle_command() -> int:
    """
    Main command handler with improved error handling and logic
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    if len(sys.argv) < 2:
        show_help()
        return 0
    
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    try:
        # Handle main commands
        if command == 'tailwindcss':
            return run_tailwind_cli(args)
            
        elif command == '--tailwindcss-help':
            return run_tailwind_cli(['--help'])
            
        elif command == 'sass-convert':
            return sass_convert(args)
            
        elif command == '--sass-convert-help':
            sass_convert_help()
            return 0
        
        elif command == 'generate-icons':
            return generate_icons(args)
            
        elif command in ['-v', '--version']:
            version = get_version()
            print(Colors.blue(f"rf-css version: {version}"))
            return 0
            
        elif command in ['-h', '--help']:
            show_help()
            return 0
            
        else:
            print(Colors.red(f"[ERROR] Unknown command: '{command}'"))
            print(Colors.yellow("[HINT] Available commands: tailwindcss, sass-convert, generate-icons"))
            print(Colors.yellow("[HINT] Use 'rf-css --help' to see all available commands"))
            return 1
            
    except KeyboardInterrupt:
        print(Colors.yellow("\n[WARNING] Command interrupted by user"))
        return 130
    except Exception as e:
        print(Colors.red(f"[ERROR] Command execution failed: {str(e)}"))
        logger.error(f"Command handler error: {e}")
        return 1


def main() -> None:
    """
    Main entry point with comprehensive error handling
    """
    try:
        # Set program name for help display
        sys.argv[0] = "rf-css"
        
        # Handle command and get exit code
        exit_code = handle_command()
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print(Colors.yellow("\n[WARNING] Program interrupted by user"), file=sys.stderr)
        sys.exit(130)
    except SystemExit:
        # Re-raise SystemExit to preserve exit codes
        raise
    except Exception as e:
        print(Colors.red(f"[ERROR] Unexpected error: {str(e)}"), file=sys.stderr)
        logger.error(f"Main execution failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()