import sys
import subprocess
from typing import Dict, Any, List, Union, Optional

from .installation import NodeJSInstaller


class DependencyChecker:
    def __init__(self):
        self.is_node = None
        self.is_npm = None
        self.is_tailwind = None
    
    def check_node(self):
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True, 
                text=True, 
                check=False
            )
            self.is_node = result.returncode == 0
                
        except (subprocess.SubprocessError, FileNotFoundError):
            self.is_node = False
    
    def check_npm(self):
        try:
            result = subprocess.run(
                ['npm', '--version'],
                capture_output=True, 
                text=True, 
                check=False
            )
            self.is_npm = result.returncode == 0
                
        except (subprocess.SubprocessError, FileNotFoundError):
            self.is_npm = False
    
    def check_tailwind(self):
        try:
            result = subprocess.run(
                ['npx', 'tailwindcss', '--version'],
                capture_output=True, 
                text=True, 
                check=False
            )
            self.is_tailwind = result.returncode == 0
                
        except (subprocess.SubprocessError, FileNotFoundError):
            self.is_tailwind = False
    
    def check_all(self):
        self.check_node()
        self.check_npm()
        self.check_tailwind()
        print(f"nodejs is '{self.is_node}' installed")
        print(f"npm is '{self.is_npm}' installed")
        print(f"tailwind is '{self.is_tailwind}' installed")
    
    def install_dependencies(self):
        if not (self.is_node and self.is_npm):
            print("Installing node and npm...")
            installer = NodeJSInstaller()
            if installer.install():
                print("node and npm installed successfully")
            else:
                print("Failed to install node and npm")
                return False
        else:
            print("node and npm are already installed")
        
        if not self.is_tailwind:
            print("Installing tailwindcss...")
            result = subprocess.run(
                ['npm', 'install', '-g', 'tailwindcss'],
                capture_output=True, 
                text=True, 
                check=False,
                timeout=60
            )
            
            if result.returncode == 0:
                print("tailwindcss installed successfully")
                return True
            else:
                print("Failed to install tailwindcss")
                return False
        else:
            print("tailwindcss is already installed")
            return True


def show_help():
    help_text = """
rf-css - ReactFlow CSS CLI Tool

Usage:
    rf-css [command] [flags] [args]

Commands:
    installation            Install dependencies (node, npm, and tailwindcss)
    check                   Check installed dependencies
    init [flags] [path]     Initialize tailwind configuration
    tailwind [args]         Access tailwindcss CLI directly
    
Flags:
    -c, --config [path]     Specify config file path (tailwind.config.js)
    -i, --input [path]      Specify input CSS file path
    -o, --output [path]     Specify output CSS file path
    -d, --default [path]    Generate default tailwindcss to output path
    -V, --verbose           Enable verbose output
    -v, --version           Show version
    -h, --help              Show this help message
    
Examples:
    rf-css installation                    # Install all dependencies
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
        result = subprocess.run(
            ['npx', 'tailwindcss'] + args,
            capture_output=True, 
            text=True, 
            check=False,
            timeout=60
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("Command timed out", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error running tailwindcss: {e}", file=sys.stderr)
        return 1


def handle_init(args):
    if not args:
        print("Error: init command requires arguments")
        return
    
    if args[0] in ['-d', '--default']:
        if len(args) < 2:
            print("Error: --default flag requires a path")
            return
            
        output_path = args[1]
        if not output_path.startswith('./'):
            print(f"Error: Path must start with './' - got '{output_path}'")
            return
            
        try:
            from ..reactflow_css.tailwindcss.Configuration import default_css
            with open(output_path, 'w') as file:
                file.write(default_css())
            print(f"Default CSS written to {output_path}")
        except Exception as e:
            print(f"Error writing default CSS: {e}")
        return
    
    # For other init commands, pass to tailwindcss
    run_tailwind_cli(['init'] + args)


def handle_command():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    checker = DependencyChecker()
    
    if command == 'installation':
        checker.check_all()
        checker.install_dependencies()
        
    elif command == 'check':
        checker.check_all()
        
    elif command == 'init':
        handle_init(args)
        
    elif command == 'tailwind':
        run_tailwind_cli(args)
        
    elif command in ['-v', '--version']:
        try:
            from ..reactflow_css.__init__ import version
            print(f"rf-css version: {version}")
        except ImportError:
            print("Version information not available")
            
    elif command in ['-h', '--help']:
        show_help()
        
    else:
        print(f"Unknown command: {command}")
        show_help()


def main():
    try:
        sys.argv[0] = "rf-css"
        handle_command()
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()