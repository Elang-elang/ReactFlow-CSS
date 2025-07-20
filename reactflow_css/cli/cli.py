import sys
import subprocess
import threading
import time
from typing import Dict, Any, List, Union, Optional

from .installation import NodeJSInstaller


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
    def red(text):
        return f"{Colors.RED}{text}{Colors.RESET}"
    
    @staticmethod
    def green(text):
        return f"{Colors.GREEN}{text}{Colors.RESET}"
    
    @staticmethod
    def yellow(text):
        return f"{Colors.YELLOW}{text}{Colors.RESET}"
    
    @staticmethod
    def blue(text):
        return f"{Colors.BLUE}{text}{Colors.RESET}"
    
    @staticmethod
    def bold(text):
        return f"{Colors.BOLD}{text}{Colors.RESET}"


class LoadingSpinner:
    def __init__(self, message="Loading", spinner_type="dots"):
        self.message = message
        self.is_spinning = False
        self.spinner_thread = None
        
        # Different spinner types
        self.spinners = {
            "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
            "circle": ["◐", "◓", "◑", "◒"],
            "snake": ["⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈"],
            "bouncing": ["⠁", "⠂", "⠄", "⠂"],
            "pulsing": ["●", "◉", "○", "◉"]
        }
        
        self.current_spinner = self.spinners.get(spinner_type, self.spinners["dots"])
        
    def _spin(self):
        """Internal method to handle the spinning animation"""
        index = 0
        while self.is_spinning:
            # Clear current line and print spinner with message
            print(f"\r{self.current_spinner[index]} {self.message}", end="", flush=True)
            index = (index + 1) % len(self.current_spinner)
            time.sleep(0.1)  # 100ms delay for smooth animation
            
    def start(self):
        """Start the loading spinner"""
        if not self.is_spinning:
            self.is_spinning = True
            self.spinner_thread = threading.Thread(target=self._spin)
            self.spinner_thread.daemon = True
            self.spinner_thread.start()
            
    def stop(self, success_message=None, error_message=None):
        """Stop the loading spinner"""
        if self.is_spinning:
            self.is_spinning = False
            if self.spinner_thread:
                self.spinner_thread.join()
            
            # Clear the spinner line
            print(f"\r{' ' * (len(self.message) + 5)}", end="", flush=True)
            print("\r", end="", flush=True)
            
            # Print final message
            if success_message:
                print(Colors.green(f"[SUCCESS] {success_message}"))
            elif error_message:
                print(Colors.red(f"[ERROR] {error_message}"))
                
    def update_message(self, new_message):
        """Update the spinner message"""
        self.message = new_message


def run_command_with_spinner(command, message, timeout=60, spinner_type="dots"):
    """
    Run a subprocess command with a loading spinner
    """
    spinner = LoadingSpinner(message, spinner_type)
    
    try:
        spinner.start()
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout
        )
        
        spinner.stop()
        
        return result
        
    except subprocess.TimeoutExpired:
        spinner.stop(error_message=f"Command timed out after {timeout} seconds")
        return None
    except Exception as e:
        spinner.stop(error_message=f"Command failed: {str(e)}")
        return None


class DependencyChecker:
    def __init__(self):
        self.is_node = None
        self.is_npm = None
        self.is_tailwind = None
    
    def check_node(self):
        result = run_command_with_spinner(
            ['node', '--version'],
            "Checking Node.js installation...",
            timeout=10,
            spinner_type="dots"
        )
        
        if result and result.returncode == 0:
            self.is_node = True
            print(Colors.green(f"[SUCCESS] Node.js found: {result.stdout.strip()}"))
        else:
            self.is_node = False
            print(Colors.red("[ERROR] Node.js not found"))
    
    def check_npm(self):
        result = run_command_with_spinner(
            ['npm', '--version'],
            "Checking npm installation...",
            timeout=10,
            spinner_type="dots"
        )
        
        if result and result.returncode == 0:
            self.is_npm = True
            print(Colors.green(f"[SUCCESS] npm found: {result.stdout.strip()}"))
        else:
            self.is_npm = False
            print(Colors.red("[ERROR] npm not found"))
    
    def check_tailwind(self):
        result = run_command_with_spinner(
            ['npx', 'tailwindcss', '--help'],
            "Checking Tailwind CSS installation...",
            timeout=60,
            spinner_type="dots"
        )
        
        if result and result.returncode == 0:
            self.is_tailwind = True
            print(Colors.green(f"[SUCCESS] Tailwind CSS found"))
        else:
            self.is_tailwind = False
            print(Colors.red("[ERROR] Tailwind CSS not found"))
    
    def check_all(self):
        print(Colors.blue("Checking dependencies..."))
        print()
        self.check_node()
        self.check_npm()  
        self.check_tailwind()
        print()
        print(Colors.blue("Dependency check completed!"))
    
    def install_dependencies(self, args):
        print()
        print(Colors.blue("Starting installation process..."))
        print()
        
        if not (self.is_node and self.is_npm):
            print("Installing Node.js and npm...")
            
            # Show spinner for Node.js installation
            spinner = LoadingSpinner("Installing Node.js and npm (this may take a few minutes)...", "pulsing")
            spinner.start()
            
            try:
                installer = NodeJSInstaller()
                success = installer.install()
                
                if success:
                    spinner.stop(success_message="Node.js and npm installed successfully")
                    # Re-check after installation
                    time.sleep(1)
                    self.check_node()
                    self.check_npm()
                else:
                    spinner.stop(error_message="Failed to install Node.js and npm")
                    return False
                    
            except Exception as e:
                spinner.stop(error_message=f"Installation error: {str(e)}")
                return False
        else:
            print(Colors.green("[SUCCESS] Node.js and npm are already installed"))
        
        if not self.is_tailwind:
            print()
            print(f"Installing Tailwind CSS {'' if '-g' not in args else 'globally'}...")
            
            result = run_command_with_spinner(
                ['npm', 'install', f'{'' if '-g' not in args else '-g'}', 'tailwindcss@3.4.17'],
                "Installing Tailwind CSS (this may take up to 60 seconds)...",
                timeout=60,
                spinner_type="snake"
            )
            
            if result and result.returncode == 0:
                print(Colors.green("[SUCCESS] Tailwind CSS installed successfully"))
                # Re-check tailwind installation
                time.sleep(1)
                self.check_tailwind()
                return True
            else:
                print(Colors.red("[ERROR] Failed to install Tailwind CSS"))
                if result and result.stderr:
                    print(Colors.red(f"Error details: {result.stderr.strip()}"))
                return False
        else:
            print(Colors.green("[SUCCESS] Tailwind CSS is already installed"))
            return True


def show_help():
    help_text = """
rf-css - ReactFlow-CSS CLI Tool

Usage:
    rf-css [command] [flags] [args]

Commands:
    installation, i                       Install dependencies (node, npm, and tailwindcss)
    check, c                              Check installed dependencies
    init [flags] [path]                   Initialize tailwind configuration
    tailwind [args]                       Access tailwindcss CLI directly
    
Flags:
    -c, --config [path]                   Specify config file path (tailwind.config.js)
    -i, --input [path]                    Specify input CSS file path
    -o, --output [path]                   Specify output CSS file path
    -d, --default [path]                  Generate default tailwindcss to output path
    -g, --global                          To install module in global scope (for tailwind)
    -V, --verbose                         Enable verbose output
    -v, --version                         Show version
    -h, --help                            Show this help message

Examples:
    rf-css installation                   # Install all dependencies
    rf-css i -g                           # Install all dependencies in global (tailwindcss)
    rf-css init -d ./output.css           # Create default CSS file
    rf-css tailwind --help                # Show tailwindcss help
    rf-css -v                             # Show version

Notes:
    - This is a beta CLI tool
    - File paths should start with './'
    """
    print(help_text)

def run_tailwind_cli(args):
    try:
        # For help commands, no need for spinner
        if '--help' in args or '-h' in args:
            result = subprocess.run(
                ['npx', 'tailwindcss'] + args,
                capture_output=True, 
                text=True, 
                check=False,
                timeout=10
            )
        else:
            # Use spinner for other tailwind commands
            result = run_command_with_spinner(
                ['npx', 'tailwindcss'] + args,
                f"Running tailwindcss {' '.join(args)}...",
                timeout=60,
                spinner_type="circle"
            )
        
        if not result:
            return 1
            
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(Colors.red(result.stderr), file=sys.stderr)
            
        return result.returncode
        
    except Exception as e:
        print(Colors.red(f"[ERROR] Error running tailwindcss: {e}"), file=sys.stderr)
        return 1


def handle_init(args):
    if not args:
        print(Colors.red("[ERROR] init command requires arguments"))
        return
    
    if args[0] in ['-d', '--default']:
        if len(args) < 2:
            print(Colors.red("[ERROR] --default flag requires a path"))
            return
            
        output_path = args[1]
        if not output_path.startswith('./'):
            print(Colors.red(f"[ERROR] Path must start with './' - got '{output_path}'"))
            return
            
        try:
            # Show spinner while generating default CSS
            spinner = LoadingSpinner("Generating default Tailwind CSS...", "bouncing")
            spinner.start()
            
            time.sleep(1)  # Small delay to show the spinner
            
            from ..tailwindcss.Configuration import default_css
            with open(output_path, 'w') as file:
                file.write(default_css())
                
            spinner.stop(success_message=f"Default CSS written to {output_path}")
            
        except Exception as e:
            spinner.stop(error_message=f"Error writing default CSS: {e}")
        return
    
    # For other init commands, pass to tailwindcss
    print("Initializing Tailwind CSS...")
    run_tailwind_cli(['init'] + args)


def handle_command():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    checker = DependencyChecker()
    
    if command in ('installation', 'i'):
        checker.check_all()
        checker.install_dependencies(args)
        
    elif command in ('check', 'c'):
        checker.check_all()
        
    elif command == 'init':
        handle_init(args)
        
    elif command == 'tailwind':
        run_tailwind_cli(args)
        
    elif command in ['-v', '--version']:
        try:
            from ..__init__ import __version__
            print(Colors.blue(f"rf-css version: {__version__}"))
        except ImportError:
            print(Colors.yellow("[WARNING] Version information not available"))
            
    elif command in ['-h', '--help']:
        show_help()
        
    else:
        print(Colors.red(f"[ERROR] Unknown command: {command}"))
        print(Colors.yellow("[WARNING] Use --help to see available commands"))


def main():
    try:
        sys.argv[0] = "rf-css"
        handle_command()
    except KeyboardInterrupt:
        print(Colors.yellow("\n[WARNING] Interrupted by user"), file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(Colors.red(f"[ERROR] {e}"), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()