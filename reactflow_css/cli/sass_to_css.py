#!/usr/bin/env python3
"""
SASS/SCSS to CSS Converter
Convert SASS/SCSS files to CSS without using argparse - pure sys implementation
"""

import os
import sys
import glob
from pathlib import Path
import sass

class SassConverter:
    def __init__(self):
        self.supported_extensions = ['.sass', '.scss']
    
    def compile_file(self, input_path, output_path=None, output_style='nested', 
                    source_map=False, include_paths=None, precision=5):
        """
        Compile single SASS/SCSS file to CSS
        
        Args:
            input_path (str): Path to input file
            output_path (str): Path to output file (optional)
            output_style (str): CSS output style ('nested', 'expanded', 'compact', 'compressed')
            source_map (bool): Generate source map
            include_paths (list): List of paths for @import
            precision (int): Decimal precision
        """
        try:
            input_path = Path(input_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"File not found: {input_path}")
            
            if input_path.suffix not in self.supported_extensions:
                raise ValueError(f"Unsupported extension: {input_path.suffix}")
            
            # Determine output path if not provided
            if output_path is None:
                output_path = input_path.with_suffix('.css')
            else:
                output_path = Path(output_path)
            
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Setup include paths
            if include_paths is None:
                include_paths = [str(input_path.parent)]
            
            # Compile SASS/SCSS
            result = sass.compile(
                filename=str(input_path),
                output_style=output_style,
                source_map_filename=str(output_path.with_suffix('.css.map')) if source_map else None,
                include_paths=include_paths,
                precision=precision
            )
            
            # Write result to file
            if isinstance(result, tuple):  # Has source map
                css_content, source_map_content = result
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(css_content)
                
                if source_map:
                    map_path = output_path.with_suffix('.css.map')
                    with open(map_path, 'w', encoding='utf-8') as f:
                        f.write(source_map_content)
                    print(f"Source map: {map_path}")
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
            
            print(f"Success: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def compile_directory(self, input_dir, output_dir=None, recursive=True, **kwargs):
        """
        Compile all SASS/SCSS files in directory
        
        Args:
            input_dir (str): Input directory
            output_dir (str): Output directory
            recursive (bool): Scan subdirectories
            **kwargs: Parameters for compile_file
        """
        input_dir = Path(input_dir)
        
        if not input_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {input_dir}")
        
        if output_dir is None:
            output_dir = input_dir
        else:
            output_dir = Path(output_dir)
        
        # Find all SASS/SCSS files
        pattern = "**/*" if recursive else "*"
        files = []
        for ext in self.supported_extensions:
            files.extend(input_dir.glob(f"{pattern}{ext}"))
        
        if not files:
            print(f"No SASS/SCSS files found in: {input_dir}")
            return False
        
        success_count = 0
        for file_path in files:
            # Skip partial files (starting with underscore)
            if file_path.name.startswith('_'):
                continue
            
            # Determine output path
            relative_path = file_path.relative_to(input_dir)
            output_path = output_dir / relative_path.with_suffix('.css')
            
            if self.compile_file(str(file_path), str(output_path), **kwargs):
                success_count += 1
        
        print(f"\nCompleted: {success_count}/{len(files)} files compiled successfully")
        return success_count > 0
    
    def watch_directory(self, input_dir, output_dir=None, **kwargs):
        """
        Watch directory for file changes (requires watchdog)
        """
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            import time
            
            class SassHandler(FileSystemEventHandler):
                def __init__(self, converter, input_dir, output_dir, **compile_kwargs):
                    self.converter = converter
                    self.input_dir = Path(input_dir)
                    self.output_dir = Path(output_dir) if output_dir else self.input_dir
                    self.compile_kwargs = compile_kwargs
                
                def on_modified(self, event):
                    if event.is_directory:
                        return
                    
                    file_path = Path(event.src_path)
                    if file_path.suffix in self.converter.supported_extensions:
                        print(f"Detected change: {file_path}")
                        
                        if file_path.name.startswith('_'):
                            # Partial file changed, compile all main files
                            self.converter.compile_directory(
                                str(self.input_dir), 
                                str(self.output_dir),
                                **self.compile_kwargs
                            )
                        else:
                            # Main file changed
                            relative_path = file_path.relative_to(self.input_dir)
                            output_path = self.output_dir / relative_path.with_suffix('.css')
                            self.converter.compile_file(
                                str(file_path), 
                                str(output_path),
                                **self.compile_kwargs
                            )
            
            handler = SassHandler(self, input_dir, output_dir, **kwargs)
            observer = Observer()
            observer.schedule(handler, str(input_dir), recursive=True)
            observer.start()
            
            print(f"Watching directory: {input_dir}")
            print("Press Ctrl+C to stop...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                print("\nStopped watching.")
            
            observer.join()
            
        except ImportError:
            print("Error: 'watchdog' package required for watch mode")
            print("Install with: pip install watchdog")
            return False

class ArgumentParser:
    """Simple argument parser without argparse"""
    
    def __init__(self):
        self.args = {}
        self.flags = set()
        self.help_requested = False
        
    def parse_args(self, args=None):
        """Parse command line arguments"""
        if args is None:
            args = sys.argv[1:]
        
        # Initialize default values
        self.args = {
            'input': None,
            'directory': None,
            'glob': None,
            'output': None,
            'style': 'nested',
            'source_map': False,
            'include_paths': [],
            'precision': 5,
            'recursive': False,
            'watch': False,
            'verbose': False
        }
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            # Help flags
            if arg in ['-h', '--help']:
                self.help_requested = True
                return self.args
            
            # Input options
            elif arg in ['-i', '--input']:
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                self.args['input'] = args[i + 1]
                i += 1
            
            elif arg == '--directory':
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                self.args['directory'] = args[i + 1]
                i += 1
            
            elif arg == '--glob':
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                self.args['glob'] = args[i + 1]
                i += 1
            
            # Output options
            elif arg in ['-o', '--output']:
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                self.args['output'] = args[i + 1]
                i += 1
            
            # Style options
            elif arg in ['-s', '--style']:
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                style = args[i + 1]
                if style not in ['nested', 'expanded', 'compact', 'compressed']:
                    raise ValueError(f"Invalid style: {style}. Must be one of: nested, expanded, compact, compressed")
                self.args['style'] = style
                i += 1
            
            # Boolean flags
            elif arg == '--source-map':
                self.args['source_map'] = True
            
            elif arg == '--recursive':
                self.args['recursive'] = True
            
            elif arg == '--watch':
                self.args['watch'] = True
            
            elif arg in ['-v', '--verbose']:
                self.args['verbose'] = True
            
            # Include path (can be used multiple times)
            elif arg == '--include-path':
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                self.args['include_paths'].append(args[i + 1])
                i += 1
            
            # Precision
            elif arg == '--precision':
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                try:
                    self.args['precision'] = int(args[i + 1])
                except ValueError:
                    raise ValueError(f"Precision must be an integer, got: {args[i + 1]}")
                i += 1
            
            else:
                raise ValueError(f"Unknown argument: {arg}")
            
            i += 1
        
        # Validate input options (mutually exclusive)
        input_count = sum(1 for x in [self.args['input'], self.args['directory'], self.args['glob']] if x is not None)
        if input_count == 0:
            raise ValueError("One input method required: -i/--input, -d/--directory, or --glob")
        elif input_count > 1:
            raise ValueError("Only one input method allowed: -i/--input, -d/--directory, or --glob")
        
        return self.args
    
    def print_help(self):
        """Print help message"""
        help_text = """
Usage: rf-css sass-convert [--verbose] [--watch] [input_option] [arguments]

A comprehensive SASS/SCSS to CSS converter powered by libsass with advanced
compilation features, source mapping, and flexible input/output handling.
  --verbose enables detailed processing information and comprehensive error traces
  --watch enables automatic recompilation when source files change (requires watchdog)

Input Options (select one):

  -i, --input <file>   - Specify single SASS/SCSS file path for conversion.
                         Supports both .sass and .scss file formats with
                         automatic syntax detection.

  --directory <path> - Specify input directory containing SASS/SCSS files
                           for batch processing. Processes all compatible
                           files in specified directory.

  --glob <pattern>     - Use glob pattern to match multiple files with
                         specific naming conventions or directory structures.
                         Supports advanced patterns like './src/**/*.scss'

Output Configuration:

  -o, --output <path>  - Specify output destination path. Can be either:
                         • File path for single file input conversion
                         • Directory path for batch processing operations
                         • Relative or absolute path formats supported

Compilation Options:

  -s, --style <format> - Set CSS output formatting style for different
                         use cases and deployment requirements:

                         nested     - Default SASS-style indented format
                                     with hierarchical structure preservation
                         expanded   - Human-readable format with separate
                                     lines and clear property separation
                         compact    - Space-efficient format with one line
                                     per CSS rule for reduced file size
                         compressed - Minified production format with
                                     whitespace removal and optimization

  --source-map         - Generate corresponding source map files (.css.map)
                         for development debugging and browser DevTools
                         integration. Maps compiled CSS back to original
                         SASS/SCSS source locations.

  --include-path <path> - Add directory path for @import and @use statement
                          resolution. Can be specified multiple times to
                          add multiple search directories for dependencies.

  --precision <number> - Set decimal precision for numeric calculations
                         in CSS output. Controls rounding of computed
                         values like percentages and measurements.
                         Default precision is 5 decimal places.

Processing Options:

  --recursive          - Enable recursive scanning of subdirectories when
                         processing directories. Searches entire directory
                         tree for SASS/SCSS files automatically.

  --watch              - Enable watch mode for continuous development
                         workflow. Monitors source files for changes and
                         automatically recompiles modified files.
                         Requires 'watchdog' Python package installation.

Other Options:

  -h, --help           - Display this comprehensive help message with
                         complete option reference and usage examples.

Output Style Examples:

  nested (default):
    .navbar {
      background-color: #333333;
      padding: 1rem; }
      .navbar .nav-item {
        color: white;
        text-decoration: none; }
        .navbar .nav-item:hover {
          color: #cccccc; }

  expanded:
    .navbar {
      background-color: #333333;
      padding: 1rem;
    }

    .navbar .nav-item {
      color: white;
      text-decoration: none;
    }

    .navbar .nav-item:hover {
      color: #cccccc;
    }

  compact:
    .navbar { background-color: #333333; padding: 1rem; }
    .navbar .nav-item { color: white; text-decoration: none; }
    .navbar .nav-item:hover { color: #cccccc; }

  compressed:
    .navbar{background-color:#333;padding:1rem}.navbar .nav-item{color:#fff;text-decoration:none}.navbar .nav-item:hover{color:#ccc}

Usage Examples:

  rf-css sass-convert -i styles.scss -o styles.css
                       Convert single SCSS file to CSS with default
                       nested formatting style.

  rf-css sass-convert -i styles.scss -o styles.css -s compressed --source-map
                       Convert single file to minified CSS with source
                       map generation for production deployment.

  rf-css sass-convert --directory ./src/scss -o ./dist/css --recursive
                       Batch process entire SCSS directory tree with
                       recursive subdirectory scanning.

  rf-css sass-convert --directory ./src/scss -o ./dist/css --watch --verbose
                       Enable watch mode with detailed logging for
                       continuous development workflow.

  rf-css sass-convert -i main.scss -o main.css --include-path ./vendors --include-path ./mixins
                       Convert with multiple custom import paths for
                       external dependencies and shared mixins.

  rf-css sass-convert --glob "./src/**/*.scss" -o ./dist --style expanded
                       Use glob pattern to process multiple SCSS files
                       with expanded output formatting.

  rf-css sass-convert -i styles.scss -o styles.css --precision 3 -s compact
                       Convert with custom numeric precision and compact
                       formatting for optimized output.

  rf-css sass-convert --directory ./themes -o ./css --recursive --source-map --watch
                       Complete development setup with directory watching,
                       source maps, and recursive processing.

Advanced Usage Patterns:

  # Development workflow with hot reloading
  rf-css sass-convert --directory ./src/styles -o ./public/css --watch --source-map --verbose

  # Production build with optimization
  rf-css sass-convert --glob "./src/**/*.scss" -o ./dist/css -s compressed

  # Library development with custom import paths  
  rf-css sass-convert -i library.scss -o library.css --include-path ./node_modules --include-path ./vendors

  # Multi-theme processing with organized output
  rf-css sass-convert --directory ./themes --recursive -o ./dist/themes -s expanded --source-map

Notes:

  • Both .sass (indented syntax) and .scss (CSS-like syntax) formats are supported
  • Watch mode requires 'watchdog' package: install with 'pip install watchdog'
  • Source maps are essential for development but should be excluded from production
  • Include paths are searched in order when resolving @import and @use statements
  • Recursive directory processing maintains relative directory structure in output
  • Glob patterns support standard wildcards: * (files), ** (directories), ? (single char)
  • Compressed output style provides maximum file size reduction for production deployment
  • Error reporting includes line numbers and file paths for efficient debugging
  • Watch mode monitors both source files and imported dependencies for changes
        """
        print(help_text.strip())